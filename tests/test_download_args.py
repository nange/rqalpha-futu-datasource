from rqalpha_futu_datasource.download import parse_codes, PERIOD_MAP, parse_args


def test_parse_codes_both_formats():
    codes = parse_codes(
        [
            "000001.XSHE",
            "SZ.000002",
            "600000.XSHG",
            "SH.600001",
            "US.AAPL",
            "00700.XHKG",
        ]
    )
    assert ("SZ", "000001") in codes
    assert ("SZ", "000002") in codes
    assert ("SH", "600000") in codes
    assert ("SH", "600001") in codes
    assert ("US", "AAPL") in codes
    assert ("HK", "00700") in codes


def test_period_map_contains_defaults():
    for p in ["1m", "3m", "5m", "1d", "1w", "1mo"]:
        assert p in PERIOD_MAP


def test_parse_args_defaults():
    args = parse_args([])
    assert "1m" in args.periods
