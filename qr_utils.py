from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q
from qrcode.image.svg import SvgPathImage


DEFAULT_URL = "https://taplink.cc/fonon"
ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def is_valid_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def build_qr(data: str, version: int | None, ecc: str, box_size: int, border: int):
    qr = qrcode.QRCode(
        version=version,
        error_correction=ERROR_LEVELS[ecc.upper()],
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=version is None)
    return qr


def build_qr_png_bytes(
    data: str,
    version: int | None = None,
    ecc: str = "M",
    box_size: int = 12,
    border: int = 4,
) -> bytes:
    qr = build_qr(data=data, version=version, ecc=ecc, box_size=box_size, border=border)
    image = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def save_qr(
    data: str,
    output: Path,
    version: int | None = None,
    ecc: str = "M",
    box_size: int = 12,
    border: int = 4,
    fmt: str = "png",
) -> Path:
    qr = build_qr(data=data, version=version, ecc=ecc, box_size=box_size, border=border)
    output.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "png":
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(output, format="PNG")
    elif fmt == "svg":
        image = qr.make_image(image_factory=SvgPathImage)
        image.save(output)
    else:
        raise ValueError("Unsupported format")

    return output
