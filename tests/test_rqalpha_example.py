import os
import time
from rqalpha import run_func
from rqalpha.api import subscribe


def init(context):
    context.codes = ["000001.XSHE"]
    subscribe(context.codes)


def handle_bar(context, bar_dict):
    now = context.now
    print(f"handle_bar at {now} codes={context.codes}, bar_dict={bar_dict['000001.XSHE']}, volume={bar_dict['000001.XSHE'].volume}, turnover={bar_dict['000001.XSHE'].total_turnover}, symbol={bar_dict['000001.XSHE'].symbol}")


def test_run_with_futu_datasource():
    os.environ["FUTU_DATA_DIR"] = os.path.abspath("tests/data")
    config = {
        "base": {
            "start_date": "2024-11-01",
            "end_date": "2024-11-06",
            "accounts": {"stock": 100000},
            "frequency": "1d",
        },
        "extra": {
            "log_level": "info",
        },
        "mod": {
            "futu_ds": {
                "enabled": True,
                "lib": "rqalpha_futu_datasource.mod_futu_ds",
                "data_dir": os.path.abspath("tests/data"),
            },
            "sys_analyser": {},
        },
    }
    run_func(init=init, handle_bar=handle_bar, config=config)
    time.sleep(3)