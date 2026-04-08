#!/usr/bin/env python3
"""
Professional QR generator with full control:
- version (1-40)
- error correction (L/M/Q/H)
- mask pattern (0-7)
- PNG or SVG output
- print-safe scaling
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse
import segno


DEFAULT_URL = "https://taplink.cc/fonon"


def is_valid_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def generate_qr(
    data: str,
    output: Path,
    version: int | None,
    ecc: str,
    mask: int | None,
    scale: int,
    border: int,
    fmt: str,
) -> Path:

    qr = segno.make(
        data,
        error=ecc.lower(),      # l m q h
        version=version,        # 1-40 or None
        mask=mask,              # 0-7 or None
        micro=False,
    )

    output.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "png":
        qr.save(
            output,
            scale=scale,
            border=border,
            dark="black",
            light="white",
        )
    elif fmt == "svg":
        qr.save(
            output,
            scale=scale,
            border=border,
            dark="black",
            light="white",
        )
    else:
        raise ValueError("Unsupported format")

    return output


def parse_args():
    parser = argparse.ArgumentParser(description="Advanced QR generator")

    parser.add_argument("--url", default=DEFAULT_URL)

    parser.add_argument("-o", "--output", default="qr.png")

    parser.add_argument("-v", "--version", type=int, default=None)

    parser.add_argument(
        "-e",
        "--ecc",
        choices=["L", "M", "Q", "H"],
        default="M",
    )

    parser.add_argument(
        "-m",
        "--mask",
        type=int,
        default=None,
        help="Mask pattern 0..7",
    )

    parser.add_argument(
        "-s",
        "--scale",
        type=int,
        default=20,
        help="Module pixel size (print quality)",
    )

    parser.add_argument(
        "-b",
        "--border",
        type=int,
        default=4,
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["png", "svg"],
        default="png",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if not is_valid_url(args.url):
        print("Invalid URL (must start with http/https)")
        return 1

    if args.version is not None and not (1 <= args.version <= 40):
        print("Version must be 1..40")
        return 1

    if args.mask is not None and not (0 <= args.mask <= 7):
        print("Mask must be 0..7")
        return 1

    output_path = Path(args.output).expanduser().resolve()

    saved = generate_qr(
        data=args.url,
        output=output_path,
        version=args.version,
        ecc=args.ecc,
        mask=args.mask,
        scale=args.scale,
        border=args.border,
        fmt=args.format,
    )

    print(f"QR saved to: {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

