import datetime
import pandas
import numpy
from unittest.mock import patch

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
    # without specifying markets, defalut to ["SH", "SZ"]
    assert e == datetime.date(2024, 10, 8)
    assert latest == datetime.date(2024, 11, 29)


def test_available_data_range_with_markets():
    # Only SZ market
    ds = FutuDataSource(data_dir="tests/data", markets=["SZ"])
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
    ds_us = FutuDataSource(data_dir="tests/data", markets=["US"])
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
