import os
from typing import Optional

from rqalpha.interface import AbstractMod
from .datasource import FutuDataSource
from .utils import rq_to_futu_code


def load_mod():
    return FutuDSMod()


class FutuDSMod(AbstractMod):
    def start_up(self, env, mod_config):
        data_dir: Optional[str] = getattr(mod_config, "futu_data_path", None)
        if data_dir is None:
            try:
                data_dir = mod_config["futu_data_path"]
            except Exception:
                data_dir = None
        hk_lot_map_path: Optional[str] = getattr(mod_config, "hk_lot_map_path", None)
        if hk_lot_map_path is None:
            try:
                hk_lot_map_path = mod_config["hk_lot_map_path"]
            except Exception:
                hk_lot_map_path = None
        hk_lot_map = getattr(mod_config, "hk_lot_map", None)
        if hk_lot_map is None:
            try:
                hk_lot_map = mod_config.get("hk_lot_map")
            except Exception:
                hk_lot_map = None
        if not data_dir:
            cfg = getattr(env, "config", None)
            base = None
            if cfg is not None:
                try:
                    base = getattr(cfg, "base", None) or cfg.get("base")
                except Exception:
                    base = None
            if base is not None:
                try:
                    bundle = getattr(base, "data_bundle_path", None) or base.get(
                        "data_bundle_path"
                    )
                except Exception:
                    bundle = None
                if bundle:
                    data_dir = bundle
        if not data_dir:
            data_dir = os.getenv("FUTU_DATA_PATH")

        markets = getattr(mod_config, "markets", None)
        if markets is None:
            try:
                markets = mod_config.get("markets")
            except Exception:
                pass

        benchmark = None
        try:
            sys_analyser = getattr(env.config.mod, "sys_analyser", None)
            if sys_analyser:
                benchmark = getattr(sys_analyser, "benchmark", None)
                if benchmark is None:
                    benchmark = sys_analyser.get("benchmark")
        except Exception:
            pass

        if benchmark:
            try:
                market, _ = rq_to_futu_code(benchmark)
                markets = [market]
            except Exception:
                pass

        env.set_data_source(
            FutuDataSource(
                data_dir=data_dir,
                hk_lot_map_path=hk_lot_map_path,
                hk_lot_map=hk_lot_map,
                markets=markets,
            )
        )

    def tear_down(self, code, exception=None):
        pass
