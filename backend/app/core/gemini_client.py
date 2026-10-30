"""Minimal Gemini REST client for the free tier (stdlib only).

The key is read from GEMINI_API_KEY or from a git-ignored .env file. The .env
may hold either `GEMINI_API_KEY=...` or a bare key on a single line.
A local counter caps daily requests so the free quota is not exceeded.
"""
import base64
import json
import os
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
# Free tier for gemini-2.5-flash allowed 20 requests/day when measured on 2026-10-30.
DEFAULT_DAILY_CAP = int(os.environ.get("GEMINI_DAILY_CAP", "20"))
USAGE_FILE = ROOT / "data" / "usage.json"


class QuotaExceeded(RuntimeError):
    pass


def load_api_key(env_path: Path = ROOT / ".env") -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key.strip()
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                name, _, value = line.partition("=")
                if name.strip() == "GEMINI_API_KEY":
                    return value.strip().strip("\"'")
            else:
                return line
    raise RuntimeError("No Gemini API key found. Set GEMINI_API_KEY or fill .env")


def _bump_usage(daily_cap: int, path: Path = None) -> int:
    path = path or USAGE_FILE
    today = date.today().isoformat()
    usage = {}
    if path.exists():
        usage = json.loads(path.read_text(encoding="utf-8"))
    if usage.get("date") != today:
        usage = {"date": today, "requests": 0}
    if usage["requests"] >= daily_cap:
        raise QuotaExceeded(f"Local daily cap of {daily_cap} requests reached")
    usage["requests"] += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(usage), encoding="utf-8")
    return usage["requests"]


def _error_detail(err) -> str:
    """Short, key-free message from a Gemini error response body."""
    try:
        msg = json.loads(err.read()).get("error", {}).get("message", "")
    except Exception:
        return "no detail"
    return " ".join(msg.split())[:700]


def build_payload(prompt, image_bytes=None, mime_type="image/png", schema=None, images=None):
    """`images` is a list of (bytes, mime) pairs; `image_bytes` is the single-image shortcut."""
    parts = [{"text": prompt}]
    pairs = list(images or [])
    if image_bytes is not None:
        pairs.insert(0, (image_bytes, mime_type))
    for data, mime in pairs:
        parts.append({"inline_data": {"mime_type": mime,
                                      "data": base64.b64encode(data).decode()}})
    payload = {"contents": [{"parts": parts}],
               "generationConfig": {"temperature": 0}}
    if schema is not None:
        payload["generationConfig"]["responseMimeType"] = "application/json"
        payload["generationConfig"]["responseSchema"] = schema
    return payload


def generate(prompt, image_bytes=None, mime_type="image/png", schema=None,
             model=DEFAULT_MODEL, daily_cap=None, retries=2, opener=urllib.request.urlopen,
             images=None):
    """Call Gemini once (with retry on 429/5xx). Returns parsed JSON if a schema
    is given, otherwise the response text."""
    _bump_usage(daily_cap if daily_cap is not None else DEFAULT_DAILY_CAP)
    body = json.dumps(build_payload(prompt, image_bytes, mime_type, schema, images)).encode()
    req = urllib.request.Request(
        ENDPOINT.format(model=model), data=body, method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": load_api_key()})
    for attempt in range(retries + 1):
        try:
            with opener(req, timeout=120) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as err:
            if err.code in (429, 500, 503) and attempt < retries:
                time.sleep(2 ** (attempt + 2))
                continue
            raise RuntimeError(f"Gemini HTTP {err.code}: {_error_detail(err)}") from None
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text) if schema is not None else text
