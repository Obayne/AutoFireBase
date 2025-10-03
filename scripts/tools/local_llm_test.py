"""
Simple local test harness for gpt4all-j using the gpt4all Python client.
If the model file is missing, it exits with a helpful message.

Usage:
  .\.venv\Scripts\python.exe .\scripts\tools\local_llm_test.py
"""

import sys
from pathlib import Path

MODEL_DIR = Path(r"C:/Dev/Models")
MODEL_NAME = "gpt4all-j.bin"  # change if you prefer a different filename
MODEL_PATH = MODEL_DIR / MODEL_NAME

PROMPT = "Summarize the AutoFire repository in 3 concise bullets for a developer."


def main():
    print(f"Python: {sys.executable}")
    print(f"Model path: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print(f"MODEL_MISSING: model file not found. Please download the model to: {MODEL_PATH}")
        return 2

    try:
        from gpt4all import GPT4All
    except Exception as e:
        print("CLIENT_MISSING: gpt4all client not installed. Run: pip install gpt4all")
        print("Error:", e)
        return 3

    try:
        print("Loading model (this may take a while)...")
        gptj = GPT4All(str(MODEL_PATH))
        print("Model loaded. Sending prompt...")
        resp = gptj.generate(PROMPT, max_tokens=256)
        print("--- RESPONSE ---")
        print(resp)
        print("--- END ---")
        return 0
    except Exception as e:
        print("RUNTIME_ERROR:", e)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
