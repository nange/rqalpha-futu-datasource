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
        data_dir: Optional[str] = getattr(mod_config, "data_dir", None)
        if data_dir is None:
            try:
                data_dir = mod_config["data_dir"]
            except Exception:
                data_dir = None
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
            data_dir = os.getenv("FUTU_DATA_DIR")
        env.set_data_source(FutuDataSource(data_dir=data_dir))

    def tear_down(self, code, exception=None):
        pass
