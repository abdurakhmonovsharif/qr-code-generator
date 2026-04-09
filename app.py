from __future__ import annotations

import base64
import os
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote, urlparse

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from qr_utils import build_qr_png_bytes, is_valid_url


app = Flask(__name__)
MEDIA_STORAGE_DIR = Path(os.environ.get("MEDIA_STORAGE_DIR", "/mnt/storage/media"))
MEDIA_PUBLIC_BASE_URL = os.environ.get("MEDIA_PUBLIC_BASE_URL", "https://media.fonon.uz").rstrip("/")
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "5"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_BYTES


def normalize_ascii(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def build_filename(value: str) -> str:
    parsed = urlparse(value)
    source_name = Path(parsed.path).stem or parsed.netloc or "qr-code"
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "-", source_name).strip("-").lower() or "qr-code"
    return f"{safe_name}-qr.png"


def slugify_filename(filename: str) -> str:
    original_name = Path(filename or "").name
    stem, ext = os.path.splitext(original_name)
    normalized_stem = normalize_ascii(stem)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized_stem).strip("-").lower() or "file"
    normalized_ext = normalize_ascii(ext.lstrip("."))
    clean_ext = re.sub(r"[^a-zA-Z0-9]+", "", normalized_ext).lower()
    return f"{slug}.{clean_ext}" if clean_ext else slug


def build_unique_media_path(filename: str) -> Path:
    candidate = MEDIA_STORAGE_DIR / filename

    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2

    while True:
        next_candidate = MEDIA_STORAGE_DIR / f"{stem}-{counter}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        counter += 1


def build_media_url(filename: str) -> str:
    return f"{MEDIA_PUBLIC_BASE_URL}/{quote(filename)}"


@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(_error):
    return jsonify({"error": f"Fayl hajmi {MAX_UPLOAD_SIZE_MB} MB dan oshmasligi kerak."}), 413


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/generate")
def generate_qr():
    payload = request.get_json(silent=True) or {}
    raw_url = str(payload.get("url", "")).strip()

    if not is_valid_url(raw_url):
        return jsonify({"error": "URL noto'g'ri. http:// yoki https:// bilan boshlang."}), 400

    image_bytes = build_qr_png_bytes(raw_url)
    image_base64 = base64.b64encode(image_bytes).decode("ascii")

    return jsonify(
        {
            "filename": build_filename(raw_url),
            "image": f"data:image/png;base64,{image_base64}",
        }
    )


@app.post("/api/upload")
def upload_file():
    uploaded_file = request.files.get("file")

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "Fayl tanlanmagan."}), 400

    stored_filename = slugify_filename(uploaded_file.filename)
    save_path = build_unique_media_path(stored_filename)

    try:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        uploaded_file.save(save_path)
    except OSError:
        return jsonify({"error": "Faylni saqlab bo'lmadi."}), 500

    public_url = build_media_url(save_path.name)
    image_bytes = build_qr_png_bytes(public_url)
    image_base64 = base64.b64encode(image_bytes).decode("ascii")

    return jsonify(
        {
            "fileUrl": public_url,
            "storedFilename": save_path.name,
            "qrFilename": build_filename(public_url),
            "image": f"data:image/png;base64,{image_base64}",
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "9191"))
    app.run(host="0.0.0.0", port=port, debug=False)
