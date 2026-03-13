import datetime
import pandas
import numpy
from unittest.mock import patch

from rqalpha_futu_datasource.datasource import FutuDataSource
from rqalpha.model.tick import TickObject
from rqalpha.interface import TRADING_CALENDAR_TYPE


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
    # without specifying markets, defalut to ["SH", "SZ"]
    assert e == datetime.date(2024, 10, 8)
    assert latest == datetime.date(2024, 11, 29)


def test_available_data_range_with_markets():
    # Only SZ market
    ds = FutuDataSource(data_dir="tests/data", market="cn")
    e, latest = ds.available_data_range("1d")
    # SZ/000001/1d.csv starts from 2024-10-08, ends 2024-11-25
    # Let's verify start/end by reading the file or checking the previous test_available_data_range which was global.
    # The global range 2024-10-01 to 2024-11-29 comes from AAPL (US) and HK probably.
    # Let's check SZ specific file content to be sure.
    # Based on previous `head` output:
    # SZ/000001/1d.csv starts 2024-10-08.
    assert e == datetime.date(2024, 10, 8)
    # SZ/000001/1d.csv ends 2024-11-25.
    assert latest == datetime.date(2024, 11, 29)

    # Check US market
    ds_us = FutuDataSource(data_dir="tests/data", market="us")
    e_us, latest_us = ds_us.available_data_range("1d")
    # US/AAPL/1d.csv starts 2024-10-01.
    assert e_us == datetime.date(2024, 10, 1)
    # US/AAPL/1d.csv ends 2024-11-29.
    assert latest_us == datetime.date(2024, 11, 29)


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


def test_board_type():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        ds = FutuDataSource(data_dir="dummy_dir")

        # Test KSH (68xxxx)
        instruments = ds.get_instruments(["688001.XSHG"])
        assert len(instruments) == 1
        assert instruments[0].board_type == "KSH"

        # Test GEM (30xxxx)
        instruments = ds.get_instruments(["300001.XSHE"])
        assert len(instruments) == 1
        assert instruments[0].board_type == "GEM"

        # Test MainBoard (00xxxx)
        instruments = ds.get_instruments(["000001.XSHE"])
        assert len(instruments) == 1
        assert instruments[0].board_type == "MainBoard"

        # Test MainBoard (60xxxx)
        instruments = ds.get_instruments(["600000.XSHG"])
        assert len(instruments) == 1
        assert instruments[0].board_type == "MainBoard"


def test_history_bars_single_field():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 6, 15)

    # Test datetime field (should be uint64)
    arr_dt = ds.history_bars(
        ins,
        2,
        "1d",
        fields="datetime",
        dt=dt,
    )
    assert arr_dt is not None
    assert isinstance(arr_dt, numpy.ndarray)
    assert arr_dt.dtype == numpy.uint64
    assert len(arr_dt) == 2
    assert arr_dt[-1] == 20241105000000

    # Test float field (should be float64)
    arr_close = ds.history_bars(
        ins,
        2,
        "1d",
        fields="close",
        dt=dt,
    )
    assert arr_close is not None
    assert isinstance(arr_close, numpy.ndarray)
    assert arr_close.dtype == numpy.float64
    assert len(arr_close) == 2
    assert numpy.isclose(arr_close[-1], 11.052)


def test_history_bars_multi_fields():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 6, 15)

    # Test multiple fields mixing datetime and floats
    fields = ["datetime", "open", "close", "volume"]
    arr = ds.history_bars(
        ins,
        2,
        "1d",
        fields=fields,
        dt=dt,
    )

    assert arr is not None
    assert isinstance(arr, numpy.ndarray)

    # Check if it is a structured array
    assert arr.dtype.names == tuple(fields)

    # Check individual field types in the structured array
    assert arr.dtype["datetime"] == numpy.uint64
    assert arr.dtype["open"] == numpy.float64
    assert arr.dtype["close"] == numpy.float64
    assert arr.dtype["volume"] == numpy.float64

    # Check values
    assert len(arr) == 2
    # Check last record values
    last_record = arr[-1]
    assert last_record["datetime"] == 20241105000000
    assert numpy.isclose(last_record["close"], 11.052)


def test_get_trading_calendars():
    ds = FutuDataSource(data_dir="tests/data")
    calendars = ds.get_trading_calendars()
    assert TRADING_CALENDAR_TYPE.CN_STOCK in calendars
    assert isinstance(calendars[TRADING_CALENDAR_TYPE.CN_STOCK], pandas.DatetimeIndex)
    # Check if some known dates are in the calendar
    assert pandas.Timestamp("2024-11-05") in calendars[TRADING_CALENDAR_TYPE.CN_STOCK]


def test_get_exchange_rate():
    ds = FutuDataSource(data_dir="tests/data")
    rate = ds.get_exchange_rate("000001.XSHE", datetime.date(2024, 11, 5))
    assert rate == 1.0


def test_get_yield_curve():
    ds = FutuDataSource(data_dir="tests/data")
    curve = ds.get_yield_curve(
        pandas.Timestamp("2024-01-01"), pandas.Timestamp("2024-01-02")
    )
    assert isinstance(curve, pandas.DataFrame)
    assert curve.empty


def test_get_dividend():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    div = ds.get_dividend(ins)
    assert div is None


def test_get_split():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    split = ds.get_split(ins)
    assert split is None


def test_is_st_stock():
    ds = FutuDataSource(data_dir="tests/data")
    res = ds.is_st_stock(
        "000001.XSHE", [pandas.Timestamp("2024-11-04"), pandas.Timestamp("2024-11-05")]
    )
    assert res == [False, False]


def test_get_instruments_no_args():
    ds = FutuDataSource(data_dir="tests/data")
    instruments = ds.get_instruments()
    assert isinstance(instruments, list)
    # With default market='cn', it should return SH/SZ instruments
    assert len(instruments) > 0
    found_obids = {i.order_book_id for i in instruments}
    assert "000001.XSHE" in found_obids


def test_hk_lot_map_config():
    # Test hk_lot_map dict
    ds = FutuDataSource(data_dir="tests/data", hk_lot_map={"00700": 100})
    assert ds._hk_lot_map["00700"] == 100


def test_hk_lot_map_file(tmp_path):
    # Create a dummy csv
    p = tmp_path / "hk_lots.csv"
    p.write_text("code,lot\n00700,500\n", encoding="utf-8")

    ds = FutuDataSource(data_dir="tests/data", hk_lot_map_path=str(p))
    assert ds._hk_lot_map["00700"] == 500


def test_get_instruments_passes_correct_params():
    # Verify that FutuDataSource constructs the correct dictionary
    # regardless of whether Instrument class respects it in this environment
    with patch("rqalpha_futu_datasource.datasource.Instrument") as mock_ins:
        with patch("os.path.exists", return_value=True):
            ds = FutuDataSource(data_dir="dummy")
            ds.get_instruments(["688001.XSHG"])

            assert mock_ins.call_count == 1
            args, _ = mock_ins.call_args
            dic = args[0]
            assert dic["board_type"] == "KSH"
            assert dic["round_lot"] == 200


def test_get_instruments_details():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        ds = FutuDataSource(
            data_dir="tests/data",
            hk_lot_map_path="tests/data/hk_lot_map.csv",
            market=["cn", "hk", "us"],
        )

        # Test A-Share (SHE)
        ins_sz = ds.get_instruments(["000001.XSHE"])[0]
        assert ins_sz.order_book_id == "000001.XSHE"
        assert ins_sz.symbol == "000001"
        assert ins_sz.exchange == "XSHE"
        assert ins_sz.round_lot == 100
        assert ins_sz.min_order_quantity == 100
        assert ins_sz.order_step_size == 100
        assert ins_sz.market.name == "CN"

        # Test A-Share (SHG)
        ins_sh = ds.get_instruments(["600000.XSHG"])[0]
        assert ins_sh.order_book_id == "600000.XSHG"
        assert ins_sh.exchange == "XSHG"
        assert ins_sh.round_lot == 100
        assert ins_sz.min_order_quantity == 100
        assert ins_sz.order_step_size == 100

        # Test HK
        ins_hk = ds.get_instruments(["00700.XHKG"])[0]
        assert ins_hk.order_book_id == "00700.XHKG"
        assert ins_hk.exchange == "XHKG"
        assert ins_hk.market.name == "HK"
        assert ins_hk.round_lot == 200
        assert ins_hk.min_order_quantity == 200
        assert ins_hk.order_step_size == 200

        # Test US
        ins_us = ds.get_instruments(["AAPL.XNAS"])[0]
        assert ins_us.order_book_id == "AAPL.XNAS"
        assert ins_us.exchange == "XNAS"
        if hasattr(ins_us.market, "name"):
            assert ins_us.market.name == "US"
        else:
            assert ins_us.market == "US"
        assert ins_us.round_lot == 1
        assert ins_us.min_order_quantity == 1
        assert ins_us.order_step_size == 1

        # Test KSH special logic
        ins_ksh = ds.get_instruments(["688306.XSHG"])[0]
        assert ins_ksh.board_type == "KSH"
        # 对于科创板，rqalpha 的 Instrument.round_lot 属性会强制返回 1
        # 但 min_order_quantity 会使用传入的 round_lot 值（200）
        assert ins_ksh.round_lot == 1
        assert ins_ksh.min_order_quantity == 200
        assert ins_ksh.order_step_size == 1


def test_get_instruments_file_not_found():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        ds = FutuDataSource(data_dir="dummy_dir")
        instruments = ds.get_instruments(["000001.XSHE"])
        assert len(instruments) == 0


def test_get_instruments_no_args_returns_all():
    # tests/data has HK, SH, SZ, US data
    ds = FutuDataSource(data_dir="tests/data", market=["cn", "hk", "us"])
    instruments = ds.get_instruments()

    assert len(instruments) > 0
    # Expected order book ids based on folder structure
    expected_obids = {"00700.XHKG", "600000.XSHG", "000001.XSHE", "AAPL.XNAS"}

    found_obids = {i.order_book_id for i in instruments}

    # Check if all expected are found
    for obid in expected_obids:
        assert obid in found_obids, f"{obid} not found in {found_obids}"


def test_get_instruments_with_market_filter_init():
    # Initialize with only 'cn' market
    ds = FutuDataSource(data_dir="tests/data", market="cn")
    instruments = ds.get_instruments()

    found_obids = {i.order_book_id for i in instruments}

    # Should contain SH/SZ
    assert "000001.XSHE" in found_obids
    assert "600000.XSHG" in found_obids

    # Should NOT contain HK or US
    assert "00700.XHKG" not in found_obids
    assert "AAPL.XNAS" not in found_obids


def test_get_instruments_id_or_syms_with_market_check():
    # Initialize with only 'cn' market
    ds = FutuDataSource(data_dir="tests/data", market="cn")

    # Request mix of CN, HK, US
    req_list = ["000001.XSHE", "00700.XHKG", "AAPL.XNAS"]
    instruments = ds.get_instruments(req_list)

    found_obids = {i.order_book_id for i in instruments}

    assert "000001.XSHE" in found_obids
    assert "00700.XHKG" not in found_obids
    assert "AAPL.XNAS" not in found_obids


def test_get_instruments_us_market_default_exchange():
    # Initialize with 'us' market
    ds = FutuDataSource(data_dir="tests/data", market="us")
    instruments = ds.get_instruments()

    found_obids = {i.order_book_id for i in instruments}
    # My logic defaults US market symbols to XNAS
    assert "AAPL.XNAS" in found_obids
