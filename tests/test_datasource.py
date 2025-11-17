import datetime
import pandas
import numpy

from rqalpha_futu_datasource.datasource import FutuDataSource


class DummyInstrument:
    def __init__(self, order_book_id: str):
        self.order_book_id = order_book_id


def test_history_bars_daily():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 6)
    arr = ds.history_bars(ins, 2, "1d", ["datetime", "open", "close"], dt, skip_suspended=True)
    assert arr is not None
    assert len(arr) == 2
    assert arr.dtype.names == ("datetime", "open", "close")
    assert int(arr[-1]["datetime"]) == 20241105000000


def test_get_bar_daily():
    ds = FutuDataSource(data_dir="tests/data")
    ins = DummyInstrument("000001.XSHE")
    dt = datetime.datetime(2024, 11, 5)
    bar = ds.get_bar(ins, dt, "1d")
    assert isinstance(bar, dict)
    assert bar["close"] == 10.7


def test_is_suspended():
    ds = FutuDataSource(data_dir="tests/data")
    res = ds.is_suspended("000001.XSHE", [pandas.Timestamp("2024-11-04"), pandas.Timestamp("2024-11-05")])
    assert res == [True, False]


def test_available_data_range():
    ds = FutuDataSource(data_dir="tests/data")
    e, l = ds.available_data_range("1d")
    assert e.date() == datetime.date(2024, 11, 1)
    assert l.date() == datetime.date(2024, 11, 5)