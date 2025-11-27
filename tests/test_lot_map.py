import os
from rqalpha_futu_datasource.datasource import FutuDataSource


def test_round_lot_hk_by_dict():
    ds = FutuDataSource(data_dir="tests/data", hk_lot_map={"00700": 200})
    assert ds._get_round_lot("XHKG", "00700") == 200


def test_round_lot_hk_by_csv():
    path = os.path.abspath("tests/data/hk_lot_map.csv")
    ds = FutuDataSource(data_dir="tests/data", hk_lot_map_path=path)
    assert ds._get_round_lot("XHKG", "00700") == 200


def test_round_lot_priority_dict_over_csv():
    path = os.path.abspath("tests/data/hk_lot_map.csv")
    ds = FutuDataSource(
        data_dir="tests/data", hk_lot_map_path=path, hk_lot_map={"00700": 400}
    )
    assert ds._get_round_lot("XHKG", "00700") == 400
