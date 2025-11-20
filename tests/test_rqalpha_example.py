import os
from rqalpha import run_func
from rqalpha.api import subscribe, history_bars


def init(context):
    context.codes = ["000001.XSHE", "600000.XSHG", "00700.XHKG", "AAPL.XNAS"]
    subscribe(context.codes)


def handle_bar(context, bar_dict):
    now = context.now
    daily_2 = history_bars(
        "000001.XSHE",
        2,
        "1d",
        include_now=False,
    )
    print(f"last 2 daily bars for 000001.XSHE at {now}: {daily_2}")

    print(
        f"handle_bar at {now} bar_dict={bar_dict['000001.XSHE']}, volume={bar_dict['000001.XSHE'].volume}, turnover={bar_dict['000001.XSHE'].total_turnover}, symbol={bar_dict['000001.XSHE'].symbol}"
    )
    print(
        f"handle_bar at {now} bar_dict={bar_dict['600000.XSHG']}, volume={bar_dict['600000.XSHG'].volume}, turnover={bar_dict['600000.XSHG'].total_turnover}, symbol={bar_dict['600000.XSHG'].symbol}"
    )
    print(
        f"handle_bar at {now} bar_dict={bar_dict['00700.XHKG']}, volume={bar_dict['00700.XHKG'].volume}, turnover={bar_dict['00700.XHKG'].total_turnover}, symbol={bar_dict['00700.XHKG'].symbol}"
    )
    print(
        f"handle_bar at {now} bar_dict={bar_dict['AAPL.XNAS']}, volume={bar_dict['AAPL.XNAS'].volume}, turnover={bar_dict['AAPL.XNAS'].total_turnover}, symbol={bar_dict['AAPL.XNAS'].symbol}"
    )


def test_run_with_futu_datasource():
    config = {
        "base": {
            "start_date": "2024-11-01",
            "end_date": "2024-11-03",
            "accounts": {"stock": 100000},
            "frequency": "1m",
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
