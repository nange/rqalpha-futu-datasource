import os
from rqalpha import run_func
from rqalpha.api import subscribe, history_bars


def init(context):
    context.codes = ["000001.XSHE", "600000.XSHG", "00700.XHKG", "AAPL.XNAS"]
    subscribe(context.codes)


def handle_bar(context, bar_dict):
    now = context.now
    assert now.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 15:00:00"

    daily_2 = history_bars(
        "000001.XSHE",
        2,
        "1d",
        fields=["datetime", "close"],
        include_now=False,
    )
    assert len(daily_2) == 2

    last = daily_2[-1]
    assert (
        f"{str(last['datetime'])[0:4]}-{str(last['datetime'])[4:6]}-{str(last['datetime'])[6:8]} {str(last['datetime'])[8:10]}:{str(last['datetime'])[10:12]}:{str(last['datetime'])[12:14]}"
        == "2024-10-31 00:00:00"
    )
    assert float(last["close"]) == 10.782

    obj = bar_dict["000001.XSHE"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 00:00:00"
    assert float(obj.open) == 10.782
    assert float(obj.high) == 10.952
    assert float(obj.low) == 10.742
    assert float(obj.close) == 10.832
    assert float(obj.volume) == 158981111.0
    assert float(obj.total_turnover) == 1821423447.06

    obj = bar_dict["600000.XSHG"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 00:00:00"
    assert float(obj.open) == 9.45
    assert float(obj.high) == 9.59
    assert float(obj.low) == 9.36
    assert float(obj.close) == 9.53
    assert float(obj.volume) == 43939258.0
    assert float(obj.total_turnover) == 435757873.0

    obj = bar_dict["00700.XHKG"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 00:00:00"
    assert float(obj.open) == 401.5
    assert float(obj.high) == 417.9
    assert float(obj.low) == 401.5
    assert float(obj.close) == 414.7
    assert float(obj.volume) == 21086569.0
    assert float(obj.total_turnover) == 8772957316.0

    obj = bar_dict["AAPL.XNAS"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 00:00:00"
    assert float(obj.open) == 219.728380867
    assert float(obj.high) == 224.088840443
    assert float(obj.low) == 219.037270399
    assert float(obj.close) == 221.662495776
    assert float(obj.volume) == 65276741.0
    assert float(obj.total_turnover) == 14544469827.0


def handle_bar_1m(context, bar_dict):
    daily_2 = history_bars(
        "000001.XSHE",
        2,
        "1d",
        fields=["datetime", "close"],
        include_now=False,
    )
    assert len(daily_2) == 2

    last = daily_2[-1]
    assert (
        f"{str(last['datetime'])[0:4]}-{str(last['datetime'])[4:6]}-{str(last['datetime'])[6:8]} {str(last['datetime'])[8:10]}:{str(last['datetime'])[10:12]}:{str(last['datetime'])[12:14]}"
        == "2024-10-31 00:00:00"
    )
    assert float(last["close"]) == 10.782

    now = context.now
    if now.strftime("%Y-%m-%d %H:%M:%S") != "2024-11-01 09:31:00":
        return

    obj = bar_dict["000001.XSHE"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 09:31:00"
    assert float(obj.open) == 10.772
    assert float(obj.high) == 10.792
    assert float(obj.low) == 10.772
    assert float(obj.close) == 10.792
    assert float(obj.volume) == 2425320.0
    assert float(obj.total_turnover) == 27597021.81

    obj = bar_dict["600000.XSHG"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 09:31:00"
    assert float(obj.open) == 9.45
    assert float(obj.high) == 9.48
    assert float(obj.low) == 9.43
    assert float(obj.close) == 9.47
    assert float(obj.volume) == 1693988.0
    assert float(obj.total_turnover) == 16708452.0

    obj = bar_dict["00700.XHKG"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 09:31:00"
    assert float(obj.open) == 401.5
    assert float(obj.high) == 406.3
    assert float(obj.low) == 401.5
    assert float(obj.close) == 406.1
    assert float(obj.volume) == 285100.0
    assert float(obj.total_turnover) == 116670900.0

    obj = bar_dict["AAPL.XNAS"]
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 09:31:00"
    assert float(obj.open) == 219.728380867
    assert float(obj.high) == 220.58853994
    assert float(obj.low) == 219.037270399
    assert float(obj.close) == 220.190778519
    assert float(obj.volume) == 1869295.0
    assert float(obj.total_turnover) == 412994919.211


def test_run_with_futu_datasource():
    config = {
        "base": {
            "start_date": "2024-11-01",
            "end_date": "2024-11-01",
            "accounts": {"stock": 100000},
            "frequency": "1d",
            # "data_bundle_path": os.path.abspath("tests/data"),
        },
        "extra": {
            "log_level": "info",
        },
        "mod": {
            "futu_ds": {
                "enabled": True,
                "lib": "rqalpha_futu_datasource.mod_futu_ds",
                "futu_data_path": os.path.abspath("tests/data"),
            },
            "sys_analyser": {},
        },
    }
    run_func(init=init, handle_bar=handle_bar, config=config)


def test_run_with_futu_datasource_1m():
    config = {
        "base": {
            "start_date": "2024-11-01",
            "end_date": "2024-11-01",
            "accounts": {"stock": 100000},
            "frequency": "1m",
        },
        "extra": {
            "log_level": "info",
        },
        "mod": {
            "futu_ds": {
                "enabled": True,
                "lib": "rqalpha_futu_datasource.mod_futu_ds",
                "futu_data_path": os.path.abspath("tests/data"),
            },
            "sys_analyser": {},
        },
    }
    run_func(init=init, handle_bar=handle_bar_1m, config=config)
