from __future__ import annotations

import base64
import os
import re
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request

from qr_utils import build_qr_png_bytes, is_valid_url


app = Flask(__name__)


def build_filename(url: str) -> str:
    parsed = urlparse(url)
    hostname = parsed.netloc or "qr-code"
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "-", hostname).strip("-").lower() or "qr-code"
    return f"{safe_name}-qr.png"


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "9191"))
    app.run(host="0.0.0.0", port=port, debug=False)
