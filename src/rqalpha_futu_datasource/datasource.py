"""
RQAlpha 的 Futu DataSource 实现。

该模块提供了实现 RQAlpha 的主要数据源类
使用Futu API获取市场数据的数据源接口。
"""

from typing import Optional, List, Dict, Tuple, Iterable, Sequence
import datetime

from rqalpha.interface import AbstractDataSource, Instrument, TRADING_CALENDAR_TYPE
from rqalpha.model import BarObject, TickObject


import pandas
import numpy


class FutuDataSource(AbstractDataSource):
    """
    在扩展模块中，可以通过调用 ``env.set_data_source`` 来替换rqalpha默认的数据源。
    """

    def __init__(self, data_dir: str | None = None):
        import os
        from .utils import rq_to_futu_code, futu_path, dt_to_int

        self._data_dir = (
            data_dir or os.getenv("FUTU_DATA_DIR") or os.path.join(os.getcwd(), "data")
        )
        self._rq_to_futu_code = rq_to_futu_code
        self._futu_path = futu_path
        self._dt_to_int = dt_to_int
        self._cache: Dict[Tuple[str, str], pandas.DataFrame] = {}

    def _load_df(self, order_book_id: str, frequency: str) -> pandas.DataFrame | None:
        market, symbol = self._rq_to_futu_code(order_book_id)
        path = self._futu_path(self._data_dir, market, symbol, frequency)
        try:
            df = pandas.read_csv(path)
        except Exception:
            return None
        if "time_key" not in df.columns:
            return None
        df = df.rename(columns={"turnover": "total_turnover"})
        df["datetime"] = pandas.to_datetime(df["time_key"])
        df = df[
            ["datetime", "open", "high", "low", "close", "volume", "total_turnover"]
        ].copy()
        df.sort_values("datetime", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def get_instruments(
        self,
        id_or_syms: Iterable[str] | None = None,
        types: Iterable[str] | None = None,
    ) -> Iterable[Instrument]:
        """
        获取 instrument，
        可指定 order_book_id 或 symbol 或 instrument type，id_or_syms 优先级高于 types，
        id_or_syms 和 types 均为 None 时返回全部 instruments
        """
        from rqalpha.const import INSTRUMENT_TYPE
        import os

        instruments: list[Instrument] = []
        if id_or_syms:
            for s in id_or_syms:
                try:
                    code, exch = s.split(".")
                except Exception:
                    code, exch = s, ""
                exch = exch.upper()
                if exch not in ("XSHE", "XSHG", "XHKG", "XNAS", "XNYS"):
                    # 默认按 A 股处理
                    exch = "XSHE"
                market, symbol = self._rq_to_futu_code(f"{code}.{exch}")
                # 若对应数据文件不存在，则跳过
                daily_path = self._futu_path(self._data_dir, market, symbol, "1d")
                minute_path = self._futu_path(self._data_dir, market, symbol, "1m")
                if not (os.path.exists(daily_path) or os.path.exists(minute_path)):
                    continue
                dic = {
                    "order_book_id": f"{code}.{exch}",
                    "symbol": code,
                    "round_lot": 100,
                    "exchange": exch,
                    "type": INSTRUMENT_TYPE.CS.name,
                    "listed_date": "1990-01-01",
                    "de_listed_date": "2999-12-31",
                }
                instruments.append(Instrument(dic))
            return instruments
        # 简化实现：当未指定 id_or_syms 时返回空列表
        return instruments

    def _collect_trading_days(self) -> pandas.DatetimeIndex:
        from pathlib import Path

        days = []
        root = Path(self._data_dir)
        for p in root.rglob("1d.csv"):
            try:
                df = pandas.read_csv(p)
            except Exception:
                continue
            if "time_key" not in df.columns:
                continue
            ts = pandas.to_datetime(df["time_key"]).dt.normalize()
            if "volume" in df.columns:
                mask = df["volume"].astype(float) > 0.0
                ts = ts[mask]
            days.extend(ts.tolist())
        if not days:
            return pandas.DatetimeIndex([])
        idx = pandas.DatetimeIndex(sorted(set(days)))
        return idx

    def get_trading_calendars(
        self,
    ) -> Dict[TRADING_CALENDAR_TYPE, pandas.DatetimeIndex]:
        cal = self._collect_trading_days()
        return {TRADING_CALENDAR_TYPE.EXCHANGE: cal}

    def get_trading_calendar(self) -> pandas.DatetimeIndex:
        return self._collect_trading_days()

    def get_yield_curve(
        self,
        start_date: pandas.Timestamp,
        end_date: pandas.Timestamp,
        tenor: str = None,
    ) -> pandas.DataFrame:
        return pandas.DataFrame()

    def get_dividend(self, instrument: Instrument) -> numpy.ndarray:
        """
        获取股票/基金分红信息
        注意：回测不用实现
        """
        raise NotImplementedError

    def get_split(self, instrument: Instrument) -> numpy.ndarray:
        """
        获取拆股信息
        注意：回测不用实现
        """
        raise NotImplementedError

    def get_bar(
        self, instrument: Instrument, dt: datetime.datetime, frequency: str
    ) -> numpy.ndarray | dict:
        """
        根据 dt 来获取对应的 Bar 数据

        :param instrument: 合约对象
        :type instrument: :class:`~Instrument`

        :param datetime.datetime dt: calendar_datetime

        :param str frequency: 周期频率，`1d` 表示日周期, `1m` 表示分钟周期
        :return: `numpy.ndarray` | `dict`
        """
        if frequency not in ("1d", "1m"):
            raise ValueError("unsupported frequency")
        key = (instrument.order_book_id, frequency)
        df = self._cache.get(key)
        if df is None:
            df = self._load_df(instrument.order_book_id, frequency)
            if df is None:
                return None
            self._cache[key] = df
        if frequency == "1d":
            target = pandas.Timestamp(dt.date())
            row = df[df["datetime"].dt.date == target.date()]
        else:
            target = pandas.Timestamp(dt)
            row = df[df["datetime"] == target]
        if row.empty:
            return None
        # fields = ["datetime", "open", "high", "low", "close", "volume", "total_turnover"]
        daily = frequency == "1d"
        ts_int = self._dt_to_int(row.iloc[0]["datetime"].to_pydatetime(), daily)
        values = {
            "datetime": ts_int,
            "open": float(row.iloc[0]["open"]),
            "high": float(row.iloc[0]["high"]),
            "low": float(row.iloc[0]["low"]),
            "close": float(row.iloc[0]["close"]),
            "volume": float(row.iloc[0]["volume"]),
            "total_turnover": float(row.iloc[0]["total_turnover"]),
        }
        return values

    def get_open_auction_bar(
        self, instrument: Instrument, dt: datetime.datetime
    ) -> BarObject:
        """
        获取指定资产当日的集合竞价 Bar 数据，该 Bar 数据应包含的字段有：
            datetime, open, limit_up, limit_down, volume, total_turnover
        注意：回测不用实现
        """
        raise NotImplementedError

    def get_open_auction_volume(
        self, instrument: Instrument, dt: datetime.datetime
    ) -> float:
        """
        获取指定资产当日的集合竞价成交量
        注意：回测不用实现
        """
        raise NotImplementedError

    def get_settle_price(self, instrument: Instrument, date: datetime.date) -> float:
        """
        获取期货品种在 date 的结算价
        注意：回测不用实现
        """
        raise NotImplementedError

    def history_bars(
        self,
        instrument: Instrument,
        bar_count: int,
        frequency: str,
        fields: str,
        dt: datetime.datetime,
        skip_suspended: bool = True,
        include_now: bool = False,
        adjust_type: str = "pre",
        adjust_orig: Optional[datetime.datetime] = None,
    ) -> numpy.ndarray | None:
        """
        获取历史数据

        :param instrument: 合约对象
        :type instrument: :class:`~Instrument`

        :param int bar_count: 获取的历史数据数量
        :param str frequency: 周期频率，`1d` 表示日周期, `1m` 表示分钟周期
        :param str fields: 返回数据字段

        =========================   ===================================================
        fields                      字段名
        =========================   ===================================================
        datetime                    时间戳
        open                        开盘价
        high                        最高价
        low                         最低价
        close                       收盘价
        volume                      成交量
        total_turnover              成交额
        datetime                    int类型时间戳
        open_interest               持仓量（期货专用）
        basis_spread                期现差（股指期货专用）
        settlement                  结算价（期货日线专用）
        prev_settlement             结算价（期货日线专用）
        =========================   ===================================================

        :param datetime.datetime dt: 时间
        :param bool skip_suspended: 是否跳过停牌日
        :param bool include_now: 是否包含当天最新数据
        :param str adjust_type: 复权类型，'pre', 'none', 'post'
        :param datetime.datetime adjust_orig: 复权起点；

        :return: `Optional[numpy.ndarray]`, fields 不合法时返回 None

        """
        if frequency not in ("1d", "1m"):
            raise ValueError("unsupported frequency")
        if adjust_type not in ("pre", "none", "post"):
            raise ValueError("invalid adjust_type")
        if adjust_type != "pre":
            raise ValueError("only pre adjust supported")
        key = (instrument.order_book_id, frequency)
        df = self._cache.get(key)
        if df is None:
            df = self._load_df(instrument.order_book_id, frequency)
            if df is None:
                return None
            self._cache[key] = df
        if frequency == "1d":
            cutoff_date = dt.date()
            data = df
            if skip_suspended:
                data = data[data["volume"] > 0]
            dates = pandas.Series(data["datetime"].dt.date)
            uniq = sorted(set(dates.tolist()))
            next_days = [d for d in uniq if d > cutoff_date]
            if include_now:
                boundary = cutoff_date
                mask = data["datetime"].dt.date <= boundary
            else:
                boundary = min(next_days) if next_days else cutoff_date
                mask = data["datetime"].dt.date < boundary
        else:
            cutoff = pandas.Timestamp(dt)
            mask = df["datetime"] < cutoff
            if include_now:
                mask = df["datetime"] <= cutoff
        if frequency == "1d":
            data = data.loc[mask]
        else:
            data = df.loc[mask]
            if skip_suspended:
                data = data[data["volume"] > 0]
        data = data.tail(bar_count)
        if isinstance(fields, str):
            fields_list = [fields]
        else:
            try:
                fields_list = list(fields)
            except Exception:
                return None
        valid = {
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "total_turnover",
            "open_interest",
            "basis_spread",
            "settlement",
            "prev_settlement",
        }
        for f in fields_list:
            if f not in valid:
                return None
        daily = frequency == "1d"
        ts_col = data["datetime"].apply(
            lambda x: self._dt_to_int(x.to_pydatetime(), daily)
        )
        out = pandas.DataFrame(index=data.index)
        for f in fields_list:
            if f == "datetime":
                out[f] = ts_col
            elif f in ("open", "high", "low", "close", "volume", "total_turnover"):
                out[f] = data[f].astype(float)
            else:
                out[f] = numpy.nan
        dtype = [
            (f, numpy.float64) if f != "datetime" else ("datetime", numpy.uint64)
            for f in fields_list
        ]
        return numpy.array(list(map(tuple, out.values)), dtype=dtype)

    def history_ticks(
        self, instrument: Instrument, count: int, dt: datetime.datetime
    ) -> List[TickObject]:
        """
        获取指定合约历史 tick 对象
        注意：回测不用实现
        """
        raise NotImplementedError

    def current_snapshot(
        self, instrument: Instrument, frequency: str, dt: datetime.datetime
    ):
        """
        获得当前市场快照数据。只能在日内交易阶段调用，获取当日调用时点的市场快照数据。
        市场快照数据记录了每日从开盘到当前的数据信息，可以理解为一个动态的day bar数据。
        在目前分钟回测中，快照数据为当日所有分钟线累积而成，一般情况下，最后一个分钟线获取到的快照数据应当与当日的日线行情保持一致。
        需要注意，在实盘模拟中，该函数返回的是调用当时的市场快照情况，所以在同一个handle_bar中不同时点调用可能返回的数据不同。
        如果当日截止到调用时候对应股票没有任何成交，那么snapshot中的close, high, low, last几个价格水平都将以0表示。

        :param instrument: 合约对象
        :type instrument: :class:`~Instrument`

        :param str frequency: 周期频率，`1d` 表示日周期, `1m` 表示分钟周期
        :param datetime.datetime dt: 时间

        :return: :class:`~Snapshot`

        TODO: 此函数似乎可以实现
        """
        raise NotImplementedError

    def get_trading_minutes_for(self, instrument, trading_dt):
        """
        获取证券某天的交易时段，用于期货回测

        :param instrument: 合约对象
        :type instrument: :class:`~Instrument`

        :param datetime.datetime trading_dt: 交易日。注意期货夜盘所属交易日规则。

        :return: list[`datetime.datetime`]

        注意：回测不用实现
        """
        raise NotImplementedError

    def available_data_range(
        self, frequency: str
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """
        此数据源能提供数据的时间范围

        :param str frequency: 周期频率，`1d` 表示日周期, `1m` 表示分钟周期

        :return: (earliest, latest)
        """
        from pathlib import Path

        freq = frequency.lower()
        if freq not in ("1d", "1m"):
            raise ValueError("unsupported frequency")
        earliest: datetime.datetime | None = None
        latest: datetime.datetime | None = None
        root = Path(self._data_dir)
        for p in root.rglob(f"{freq}.csv"):
            try:
                df = pandas.read_csv(p)
            except Exception:
                continue
            if "time_key" not in df.columns:
                continue
            ts = pandas.to_datetime(df["time_key"])
            if len(ts) == 0:
                continue
            e = ts.min().to_pydatetime()
            _latest = ts.max().to_pydatetime()
            if earliest is None or e < earliest:
                earliest = e
            if latest is None or _latest > latest:
                latest = _latest
        if earliest is None or latest is None:
            raise ValueError("no data")
        return earliest.date(), latest.date()

    def get_futures_trading_parameters(self, instrument, dt):
        """
        获取期货合约的时序手续费信息
        :param instrument: 合约对象
        :type instrument: :class:`~Instrument`

        :param datetime.datetime dt: 交易日

        :return: :class:`FuturesTradingParameters`

        注意：回测不用实现
        """
        raise NotImplementedError

    def get_merge_ticks(self, order_book_id_list, trading_date, last_dt=None):
        """
        获取合并的 ticks

        :param list order_book_id_list: 合约名列表
        :param datetime.date trading_date: 交易日
        :param datetime.datetime last_dt: 仅返回 last_dt 之后的时间

        :return: Iterable object of Tick

        注意：回测不用实现
        """
        raise NotImplementedError

    def get_share_transformation(self, order_book_id):
        """
        获取股票转换信息
        :param order_book_id: 合约代码
        :return: (successor, conversion_ratio), (转换后的合约代码，换股倍率)

        注意：回测不用实现
        """
        raise NotImplementedError

    def is_suspended(self, order_book_id: str, dates: Sequence) -> Sequence[bool]:
        key = (order_book_id, "1d")
        df = self._cache.get(key)
        if df is None:
            df = self._load_df(order_book_id, "1d")
            if df is None:
                return [False for _ in dates]
            self._cache[key] = df
        res: List[bool] = []
        for d in dates:
            if isinstance(d, pandas.Timestamp):
                day = d.date()
            elif isinstance(d, datetime.datetime):
                day = d.date()
            elif isinstance(d, datetime.date):
                day = d
            else:
                try:
                    day = pandas.Timestamp(d).date()
                except Exception:
                    res.append(False)
                    continue
            row = df[df["datetime"].dt.date == day]
            if row.empty:
                res.append(False)
            else:
                res.append(float(row.iloc[0]["volume"]) == 0.0)
        return res

    def is_st_stock(self, order_book_id: str, dates: Sequence) -> Sequence[bool]:
        return [False for _ in dates]

    def get_algo_bar(self, id_or_ins, start_min, end_min, dt):
        raise NotImplementedError
