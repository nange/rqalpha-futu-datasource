import os

from rqalpha.interface import AbstractMod
from .datasource import FutuDataSource


def load_mod():
    return FutuDSMod()


def _get_config(obj, key):
    val = getattr(obj, key, None)
    if val is not None:
        return val
    if hasattr(obj, "get"):
        return obj.get(key, None)
    try:
        return obj[key]
    except (TypeError, KeyError, Exception):
        return None


class FutuDSMod(AbstractMod):
    def start_up(self, env, mod_config):
        data_dir = _get_config(mod_config, "futu_data_path")
        hk_lot_map_path = _get_config(mod_config, "hk_lot_map_path")
        hk_lot_map = _get_config(mod_config, "hk_lot_map")

        if not data_dir:
            cfg = getattr(env, "config", None)
            base = _get_config(cfg, "base") if cfg else None
            bundle = _get_config(base, "data_bundle_path") if base else None
            if bundle:
                data_dir = bundle

        if not data_dir:
            data_dir = os.getenv("FUTU_DATA_PATH")

        base_config = getattr(env.config, "base", None)
        markets = _get_config(base_config, "market") if base_config else None

        if not markets:
            markets = "cn"

        env.set_data_source(
            FutuDataSource(
                data_dir=data_dir,
                hk_lot_map_path=hk_lot_map_path,
                hk_lot_map=hk_lot_map,
                market=markets,
            )
        )

    def tear_down(self, code, exception=None):
        pass
