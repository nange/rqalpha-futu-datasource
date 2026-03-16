import os
from rqalpha import run_func
from rqalpha.api import subscribe, history_bars, current_snapshot, order_shares


def init(context):
    context.codes = ["000001.XSHE", "600000.XSHG", "00700.XHKG", "AAPL.XNAS"]
    context.order_count = 0
    subscribe(context.codes)


def handle_bar(context, bar_dict):
    if context.order_count < 3:
        order = order_shares("000001.XSHE", 100)
        print(f"Order placed in handle_bar: {order}")
        assert order is not None
        assert order.order_id
        assert order.trading_datetime.date() == context.now.date()
        context.order_count += 1
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
    assert daily_2[-1]["datetime"] == 20241031000000
    assert float(daily_2[-1]["close"]) == 10.782

    weekly_2 = history_bars(
        "000001.XSHE",
        2,
        "1w",
        include_now=False,
    )
    assert len(weekly_2) == 2
    assert weekly_2[-1]["datetime"] == 20241028000000
    assert float(weekly_2[-1]["close"]) == 10.832

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
    assert float(obj.open) == 219.522968047
    assert float(obj.high) == 223.879351252
    assert float(obj.low) == 218.832503662
    assert float(obj.close) == 221.45527485
    assert float(obj.volume) == 65276741.0
    assert float(obj.total_turnover) == 14544469827.0


def handle_bar_1m(context, bar_dict):
    if context.order_count < 3:
        order = order_shares("000001.XSHE", 100)
        print(f"Order placed in handle_bar_1m: {order}")
        assert order is not None
        assert order.order_id
        assert order.trading_datetime.date() == context.now.date()
        context.order_count += 1

    daily_2 = history_bars(
        "000001.XSHE",
        2,
        "1d",
        fields=["datetime", "close"],
        include_now=False,
    )
    assert len(daily_2) == 2

    last = daily_2[-1]
    assert last["datetime"] == 20241031000000
    assert float(last["close"]) == 10.782

    now = context.now
    if now.strftime("%Y-%m-%d %H:%M:%S") != "2024-11-01 09:31:00":
        return

    minute_2 = history_bars(
        "000001.XSHE",
        4,
        "1m",
        include_now=True,
    )
    assert len(minute_2) == 4
    assert minute_2[0]["datetime"] == 20241031145800
    assert minute_2[1]["datetime"] == 20241031150000
    assert minute_2[2]["datetime"] == 20241101093000
    assert minute_2[3]["datetime"] == 20241101093100
    assert float(minute_2[0]["close"]) == 10.782
    assert float(minute_2[1]["close"]) == 10.782
    assert float(minute_2[2]["close"]) == 10.782
    assert float(minute_2[3]["close"]) == 10.792

    minute_3 = history_bars(
        "000001.XSHE",
        4,
        "3m",
        include_now=True,
    )
    assert len(minute_3) == 4
    assert minute_3[0]["datetime"] == 20241031145100
    assert minute_3[1]["datetime"] == 20241031145400
    assert minute_3[2]["datetime"] == 20241031145700
    assert minute_3[3]["datetime"] == 20241031150000
    assert float(minute_3[0]["close"]) == 10.772
    assert float(minute_3[1]["close"]) == 10.772
    assert float(minute_3[2]["close"]) == 10.782
    assert float(minute_3[3]["close"]) == 10.782

    minute_5 = history_bars(
        "000001.XSHE",
        4,
        "5m",
        include_now=True,
    )
    assert len(minute_5) == 4
    assert minute_5[0]["datetime"] == 20241031144500
    assert minute_5[1]["datetime"] == 20241031145000
    assert minute_5[2]["datetime"] == 20241031145500
    assert minute_5[3]["datetime"] == 20241031150000
    assert float(minute_5[0]["close"]) == 10.762
    assert float(minute_5[1]["close"]) == 10.772
    assert float(minute_5[2]["close"]) == 10.782
    assert float(minute_5[3]["close"]) == 10.782

    weekly_4 = history_bars(
        "000001.XSHE",
        4,
        "1w",
        include_now=True,
    )
    assert len(weekly_4) == 4
    assert weekly_4[0]["datetime"] == 20241007000000
    assert weekly_4[1]["datetime"] == 20241014000000
    assert weekly_4[2]["datetime"] == 20241021000000
    assert weekly_4[3]["datetime"] == 20241028000000
    assert float(weekly_4[0]["close"]) == 11.122
    assert float(weekly_4[1]["close"]) == 11.442
    assert float(weekly_4[2]["close"]) == 11.112
    assert float(weekly_4[3]["close"]) == 10.832

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
    assert float(obj.open) == 219.522968047
    assert float(obj.high) == 220.382323001
    assert float(obj.low) == 218.832503662
    assert float(obj.close) == 219.984933427
    assert float(obj.volume) == 1869295.0
    assert float(obj.total_turnover) == 412994919.211

    obj = current_snapshot("000001.XSHE")
    assert obj.datetime.strftime("%Y-%m-%d %H:%M:%S") == "2024-11-01 09:31:00"
    assert float(obj.open) == 10.782
    assert float(obj.high) == 10.792
    assert float(obj.low) == 10.772
    assert float(obj.last) == 10.792
    assert float(obj.volume) == 3053120.0
    assert float(obj.total_turnover) == 34741385.81


def test_run_with_futu_datasource():
    config = {
        "base": {
            "start_date": "2024-11-01",
            "end_date": "2024-11-01",
            "accounts": {"stock": 100000},
            "frequency": "1d",
            "market": ["cn", "hk", "us"],
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
                "hk_lot_map_path": os.path.abspath("tests/data/hk_lot_map.csv"),
            },
            "sys_analyser": {
                "enabled": True,
                "benchmark": "600000.XSHG",
                # "plot": True,  # 开启后，会生成回测报告图片
                # "output_file": "result.pkl", # 回测结果保存文件，默认不保存
                # "report_save_path": "backtest_report", # 回测报告保存路径目录(另外一种格式)，默认不保存
            },
            "sys_progress": {
                "enabled": True,
                "show": True,
            },
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
            "market": ["cn", "hk", "us"],
        },
        "extra": {
            "log_level": "info",
        },
        "mod": {
            "futu_ds": {
                "enabled": True,
                "lib": "rqalpha_futu_datasource.mod_futu_ds",
                "futu_data_path": os.path.abspath("tests/data"),
                "hk_lot_map_path": os.path.abspath("tests/data/hk_lot_map.csv"),
            }
        },
    }
    run_func(init=init, handle_bar=handle_bar_1m, config=config)
