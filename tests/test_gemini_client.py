import json
import pytest
from billrecon import gemini_client as gc


def test_load_key_bare_and_named(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    bare = tmp_path / "a.env"
    bare.write_text("abc123\n")
    assert gc.load_api_key(bare) == "abc123"
    named = tmp_path / "b.env"
    named.write_text('# c\nGEMINI_API_KEY="xyz"\n')
    assert gc.load_api_key(named) == "xyz"


def test_daily_cap(tmp_path):
    path = tmp_path / "usage.json"
    gc._bump_usage(2, path)
    gc._bump_usage(2, path)
    with pytest.raises(gc.QuotaExceeded):
        gc._bump_usage(2, path)


def test_payload_schema_and_image():
    p = gc.build_payload("hi", b"\x89PNG", schema={"type": "OBJECT"})
    assert p["generationConfig"]["responseMimeType"] == "application/json"
    assert len(p["contents"][0]["parts"]) == 2


def test_generate_parses_json(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "USAGE_FILE", tmp_path / "u.json")
    monkeypatch.setattr(gc, "load_api_key", lambda *a, **k: "k")

    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self):
            return json.dumps({"candidates": [{"content": {"parts": [{"text": '{"a": 1}'}]}}]}).encode()

    out = gc.generate("x", schema={"type": "OBJECT"}, opener=lambda *a, **k: Resp(),
                      daily_cap=5)
    assert out == {"a": 1}
