#!/usr/bin/env python3
"""
Professional QR generator with full control:
- version (1-40)
- error correction (L/M/Q/H)
- PNG or SVG output
"""

from __future__ import annotations

import argparse
from pathlib import Path

from qr_utils import DEFAULT_URL, is_valid_url, save_qr


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
        "-s",
        "--scale",
        type=int,
        default=20,
        help="Module pixel size",
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

    output_path = Path(args.output).expanduser().resolve()

    saved = save_qr(
        data=args.url,
        output=output_path,
        version=args.version,
        ecc=args.ecc,
        box_size=args.scale,
        border=args.border,
        fmt=args.format,
    )

    print(f"QR saved to: {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
