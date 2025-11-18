import argparse
import os
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import futu as ft

from .constants import FUTU_HOST, FUTU_PORT
from .utils import rq_to_futu_code


PERIOD_MAP = {
    "1d": ft.KLType.K_DAY,
    "1m": ft.KLType.K_1M,
    "3m": ft.KLType.K_3M,
    "5m": ft.KLType.K_5M,
    "1w": ft.KLType.K_WEEK,
    "1mo": ft.KLType.K_MON,
}


def parse_codes(raw: List[str]) -> List[Tuple[str, str]]:
    res: List[Tuple[str, str]] = []
    for c in raw:
        c = c.strip()
        if not c:
            continue
        parts = c.split(".")
        if len(parts) == 2 and parts[1].upper() in (
            "XSHG",
            "XSHE",
            "XHKG",
            "XNAS",
            "XNYS",
        ):
            market, symbol = rq_to_futu_code(c)
            res.append((market, symbol))
        elif len(parts) == 2 and parts[0].upper() in ("SH", "SZ", "HK", "US"):
            res.append((parts[0].upper(), parts[1]))
        else:
            raise ValueError("invalid code format")
    return res


def ensure_dir(root: str, market: str, symbol: str):
    Path(root, market, symbol).mkdir(parents=True, exist_ok=True)


def file_name(period: str) -> str:
    return f"{period}.csv"


def save_csv(root: str, market: str, symbol: str, period: str, df: pd.DataFrame):
    cols = ["time_key", "open", "high", "low", "close", "volume", "turnover"]
    out = df[cols].copy()
    ensure_dir(root, market, symbol)
    out.to_csv(Path(root, market, symbol, file_name(period)), index=False)


def fetch_history(
    ctx: ft.OpenQuoteContext, code: str, period: str, start: str | None, end: str | None
) -> pd.DataFrame:
    ktype = PERIOD_MAP[period]
    ret, data, page_req_key = ctx.request_history_kline(
        code,
        start=start,
        end=end,
        ktype=ktype,
        autype=ft.AuType.QFQ,
        fields=[ft.KL_FIELD.ALL],
        max_count=1000,
    )
    if ret != ft.RET_OK:
        raise RuntimeError(str(data))
    frames = [data]
    while page_req_key is not None:
        ret, data, page_req_key = ctx.request_history_kline(
            code,
            start=start,
            end=end,
            ktype=ktype,
            autype=ft.AuType.QFQ,
            fields=[ft.KL_FIELD.ALL],
            max_count=1000,
            page_req_key=page_req_key,
        )
        if ret != ft.RET_OK:
            raise RuntimeError(str(data))
        frames.append(data)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame(
        columns=["time_key", "open", "high", "low", "close", "volume", "turnover"]
    )


def download(
    root: str,
    codes: List[Tuple[str, str]],
    periods: List[str],
    start: str | None,
    end: str | None,
    host: str,
    port: int,
):
    ctx = ft.OpenQuoteContext(host=host, port=port)
    try:
        for market, symbol in codes:
            futu_code = f"{market}.{symbol}"
            for p in periods:
                df = fetch_history(ctx, futu_code, p, start, end)
                save_csv(root, market, symbol, p, df)
    finally:
        ctx.close()


def parse_args(argv: List[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=str,
        default=os.getenv("FUTU_DATA_DIR", os.path.join(os.getcwd(), "data")),
    )
    parser.add_argument("--codes", type=str, default="")
    parser.add_argument("--code-file", type=str, default="")
    parser.add_argument("--periods", type=str, default="1m,3m,5m,1d,1w,1mo")
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    parser.add_argument("--host", type=str, default=os.getenv("FUTU_HOST", FUTU_HOST))
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("FUTU_PORT", str(FUTU_PORT)))
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None):
    args = parse_args(argv)
    codes_raw: List[str] = []
    if args.codes:
        codes_raw.extend([x for x in args.codes.split(",") if x])
    if args.code_file:
        with open(args.code_file, "r", encoding="utf-8") as f:
            codes_raw.extend([line.strip() for line in f if line.strip()])
    codes = parse_codes(codes_raw)
    periods = [p.strip() for p in args.periods.split(",") if p.strip()]
    for p in periods:
        if p not in PERIOD_MAP:
            raise ValueError("unsupported period")
    download(args.data_dir, codes, periods, args.start, args.end, args.host, args.port)


if __name__ == "__main__":
    main()
