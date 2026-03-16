import pytest
from rqalpha_futu_datasource.download import parse_codes, PERIOD_MAP, parse_args
from rqalpha_futu_datasource.constants import FUTU_HOST, FUTU_PORT


def test_parse_codes_valid_formats():
    codes = parse_codes(
        [
            "000001.XSHE",
            "600000.XSHG",
            "00700.XHKG",
            "AAPL.XNAS",
        ]
    )
    # New format: (market, symbol, order_book_id)
    assert ("SZ", "000001", "000001.XSHE") in codes
    assert ("SH", "600000", "600000.XSHG") in codes
    assert ("HK", "00700", "00700.XHKG") in codes
    assert ("US", "AAPL", "AAPL.XNAS") in codes


def test_parse_codes_invalid_format():
    with pytest.raises(ValueError, match="Invalid code format"):
        parse_codes(["SZ.000002"])

    with pytest.raises(ValueError, match="Invalid code format"):
        parse_codes(["SH.600001"])

    with pytest.raises(ValueError, match="Invalid code format"):
        parse_codes(["US.AAPL"])


def test_period_map_contains_defaults():
    for p in ["1m", "3m", "5m", "1d", "1w", "1mo"]:
        assert p in PERIOD_MAP


def test_parse_args_defaults():
    args = parse_args([])
    assert "1m" in args.periods
    assert args.host == FUTU_HOST
    assert args.port == FUTU_PORT


def test_parse_args_override_host_port():
    args = parse_args(["--host", "10.0.0.2", "--port", "22222"])
    assert args.host == "10.0.0.2"
    assert args.port == 22222
