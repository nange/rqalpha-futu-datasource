import datetime
import pandas

from rqalpha_futu_datasource.datasource import FutuDataSource


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
