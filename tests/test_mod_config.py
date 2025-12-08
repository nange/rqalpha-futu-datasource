import pytest
from unittest.mock import MagicMock
from rqalpha_futu_datasource.mod_futu_ds import FutuDSMod
from rqalpha_futu_datasource.datasource import FutuDataSource


@pytest.fixture
def mod():
    return FutuDSMod()


@pytest.fixture
def env():
    return MagicMock()


@pytest.fixture
def mod_config():
    return MagicMock()


@pytest.mark.parametrize(
    "market, expected_markets",
    [
        ("cn", ["SH", "SZ"]),
        ("hk", ["HK"]),
        ("us", ["US"]),
    ],
)
def test_start_up_markets(mod, env, mod_config, market, expected_markets):
    # Mock env.config.base.market
    env.config.base.market = market

    mod.start_up(env, mod_config)

    # Verify set_data_source called with correct markets
    args, kwargs = env.set_data_source.call_args
    ds = args[0]
    assert isinstance(ds, FutuDataSource)
    assert ds._markets == expected_markets


def test_start_up_default(mod, env, mod_config):
    # env.config.base.market is missing/None
    env.config.base.market = None
    # and config.base.get returns None
    env.config.base.get.return_value = None

    mod.start_up(env, mod_config)

    args, kwargs = env.set_data_source.call_args
    ds = args[0]
    # Should default to cn -> SH, SZ
    assert isinstance(ds, FutuDataSource)
    assert ds._markets == ["SH", "SZ"]
