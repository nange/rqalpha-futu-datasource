import os
from rqalpha import run_func


def init(context):
    context.logger.info("Backtest init with Futu DataSource mod")
    context.codes = ["000001.XSHE"]


def handle_bar(context, bar_dict):
    now = context.now
    context.logger.info(f"handle_bar at {now} codes={context.codes}")
    print(f"handle_bar at {now} codes={context.codes}")


def test_run_with_futu_datasource():
    os.environ["FUTU_DATA_DIR"] = os.path.abspath("tests/data")
    config = {
        "base": {
            "start_date": "2024-11-01",
            "end_date": "2024-11-06",
            "benchmark": "000001.XSHE",
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
            }
        },
    }
    run_func(init=init, handle_bar=handle_bar, config=config)