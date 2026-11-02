"""Send one streaming coding prompt to the Kaggle Strata tunnel."""

import os
import sys
from pathlib import Path

from openai import OpenAI


def load_env(path):
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require(name):
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Missing {name}. Copy the notebook output into .env (see .env.example).", file=sys.stderr)
        raise SystemExit(1)
    return value


def main():
    load_env(Path(__file__).resolve().parents[1] / ".env")
    base_url = require("STRATA_BASE_URL")
    api_key = require("STRATA_API_KEY")
    model = os.environ.get("STRATA_MODEL", "gyro-s-strata").strip() or "gyro-s-strata"

    client = OpenAI(base_url=base_url, api_key=api_key)
    request = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Write a Python function that merges two sorted lists. Return only the function.",
            }
        ],
        "temperature": 0.7,
        "top_p": 0.8,
        "stream": True,
    }
    try:
        stream = client.chat.completions.create(**request, stream_options={"include_usage": True})
    except Exception as exc:
        # Some OpenAI-compatible servers reject stream_options. The sampling settings stay the same.
        if getattr(exc, "status_code", None) not in {400, 422}:
            raise
        stream = client.chat.completions.create(**request)

    printed = False
    for chunk in stream:
        if not chunk.choices:
            usage = getattr(chunk, "usage", None)
            if usage is not None:
                print(f"\nusage: {usage}")
            continue
        delta = chunk.choices[0].delta
        text = getattr(delta, "content", None) or ""
        if text:
            printed = True
            print(text, end="", flush=True)
    if printed:
        print()
    else:
        print("The stream ended without answer text. The model may still be starting.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
