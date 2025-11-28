import datetime
import pandas

from rqalpha_futu_datasource.datasource import FutuDataSource
from rqalpha.model.tick import TickObject


class DummyInstrument:
    def __init__(self, order_book_id: str):
        self.order_book_id = order_book_id


def test_history_bars_daily():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 6, 15)
    dt2 = datetime.datetime(2024, 11, 6)
    arr = ds.history_bars(
        ins,
        2,
        "1d",
        include_now=False,
        fields=["datetime", "open", "close"],
        dt=dt,
        skip_suspended=True,
    )
    arr2 = ds.history_bars(
        ins,
        2,
        "1d",
        include_now=False,
        fields=["datetime", "open", "close"],
        dt=dt2,
        skip_suspended=True,
    )
    assert arr is not None
    assert len(arr) == 2
    assert arr.dtype.names == ("datetime", "open", "close")
    assert int(arr[-1]["datetime"]) == 20241105000000

    assert int(arr2[-1]["datetime"]) == 20241106000000


def test_get_bar_daily():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 5)
    bar = ds.get_bar(ins, dt, "1d")
    assert isinstance(bar, dict)
    assert bar["close"] == 11.052


def test_is_suspended():
    ds = FutuDataSource(data_dir="tests/data")
    res = ds.is_suspended(
        "000001.XSHE", [pandas.Timestamp("2024-11-04"), pandas.Timestamp("2024-11-05")]
    )
    assert res == [False, False]


def test_available_data_range():
    ds = FutuDataSource(data_dir="tests/data")
    e, latest = ds.available_data_range("1d")
    assert e == datetime.date(2024, 1, 2)
    assert latest == datetime.date(2024, 12, 31)


def test_current_snapshot_minute_aggregation():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 1, 9, 35)
    tick = ds.current_snapshot(ins, "1m", dt)
    assert isinstance(tick, TickObject)
    assert tick.order_book_id == "000001.XSHE"
    assert tick.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 09:35:00"
    assert float(tick.open) == 10.782
    assert float(tick.high) == 10.802
    assert float(tick.low) == 10.752
    assert float(tick.last) == 10.752
    assert float(tick.volume) == 6306120.0
    assert float(tick.total_turnover) == 71763945.81
    assert float(tick.prev_close) == 10.782


def test_current_snapshot_minute_no_trade_returns_zero():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 1, 9, 29)
    tick = ds.current_snapshot(ins, "1m", dt)
    assert isinstance(tick, TickObject)
    assert tick.order_book_id == "000001.XSHE"
    assert float(tick.open) == 0.0
    assert float(tick.high) == 0.0
    assert float(tick.low) == 0.0
    assert float(tick.last) == 0.0
    assert float(tick.volume) == 0.0
    assert float(tick.total_turnover) == 0.0
    assert float(tick.prev_close) == 10.782


def test_current_snapshot_daily():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 1)
    tick = ds.current_snapshot(ins, "1d", dt)
    assert isinstance(tick, TickObject)
    assert tick.order_book_id == "000001.XSHE"
    assert tick.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 00:00:00"
    assert float(tick.open) == 10.782
    assert float(tick.high) == 10.952
    assert float(tick.low) == 10.742
    assert float(tick.last) == 10.832
    assert float(tick.volume) == 158981111.0
    assert float(tick.total_turnover) == 1821423447.06
    assert float(tick.prev_close) == 10.782
