import os
from typing import Optional

from rqalpha.interface import AbstractMod
from .datasource import FutuDataSource


__config__ = {
    "data_dir": None,
}


def load_mod():
    return FutuDSMod()


class FutuDSMod(AbstractMod):
    def start_up(self, env, mod_config):
        data_dir: Optional[str] = mod_config.get("data_dir")
        if not data_dir:
            data_dir = os.getenv("FUTU_DATA_DIR")
        env.set_data_source(FutuDataSource(data_dir=data_dir))

    def tear_down(self, code, exception=None):
        pass