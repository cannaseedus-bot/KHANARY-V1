#!/usr/bin/env python3
"""
gen.py — two-model adviser→coder pipeline.

Two backends:
  --http (default): calls the existing llama-server at INFER_URL (DirectML GPU, no extra install)
  --local:          loads GGUFs in-process via llama-cpp-python (needs DirectML wheel for GPU)

Usage:
    python gen.py "build a dark mode toggle"
    python gen.py --edit path/to/file.html "add a search bar to the header"
    python gen.py --patch path/to/file.js "replace hardcoded port 8080 with process.env.PORT"
    python gen.py --local "landing page for GPU inference toolkit"

Or import and call gen() directly:
    from gen import gen
    result = gen("add error handling", file="server.js", mode="edit")
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from config import INFER_URL, ADVISER_MODEL, CODER_MODEL

_adviser = None
_coder   = None


def _http_chat(messages: list, max_tokens: int = 400, temperature: float = 0.2) -> str:
    """Call the running llama-server directly — uses DirectML GPU."""
    payload = json.dumps({
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }).encode()
    req = urllib.request.Request(INFER_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def _load_models():
    global _adviser, _coder
    if _adviser is not None:
        return
    try:
        from llama_cpp import Llama
    except ImportError:
        print("llama-cpp-python not installed — run: pip install llama-cpp-python", file=sys.stderr)
        print("For DirectML GPU support: pip install llama-cpp-python "
              "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/directml",
              file=sys.stderr)
        sys.exit(1)

    print("[gen] loading adviser (Gemma)…", file=sys.stderr)
    _adviser = Llama(model_path=ADVISER_MODEL, n_ctx=2048, n_gpu_layers=-1, verbose=False)

    print("[gen] loading coder (Qwen3)…", file=sys.stderr)
    _coder = Llama(model_path=CODER_MODEL, n_ctx=4096, n_gpu_layers=-1, verbose=False)
    print("[gen] models ready", file=sys.stderr)


def gen(prompt: str, file: str | None = None, mode: str = "gen",
        max_tokens: int = 4096, backend: str = "http") -> dict:
    """
    Two-step adviser→coder generation.

    Args:
        prompt:     The task description.
        file:       Absolute path to target file (required for edit/patch).
        mode:       'gen' | 'edit' | 'patch'
        max_tokens: Max tokens for coder output.

    Returns:
        dict with keys: plan, code, written, file
    """
    if backend == "local":
        _load_models()

    def _chat(messages, max_tok, temp):
        if backend == "http":
            return _http_chat(messages, max_tokens=max_tok, temperature=temp)
        resp = _adviser.create_chat_completion(messages=messages, max_tokens=max_tok, temperature=temp)
        return resp["choices"][0]["message"]["content"]

    def _code(messages, max_tok, temp):
        if backend == "http":
            return _http_chat(messages, max_tokens=max_tok, temperature=temp)
        resp = _coder.create_chat_completion(messages=messages, max_tokens=max_tok, temperature=temp,
                                             repeat_penalty=1.28)
        return resp["choices"][0]["message"]["content"]

    # Step 1 — adviser produces a brief
    plan = ""
    try:
        plan = _chat([
            {"role": "system", "content":
             "You are a concise implementation planner. "
             "Return 5-8 short bullets covering structure, requirements, and key decisions. "
             "No code."},
            {"role": "user", "content": f"Create an implementation brief for:\n\n{prompt}"},
        ], 400, 0.2)
    except Exception as e:
        print(f"[gen] adviser step failed (continuing): {e}", file=sys.stderr)

    # Step 2 — read target file if edit/patch
    file_content = ""
    if file and mode in ("edit", "patch"):
        file_content = Path(file).read_text(encoding="utf-8")
    elif file and mode == "gen":
        try:
            file_content = Path(file).read_text(encoding="utf-8")
        except Exception:
            pass

    # Build coder prompt
    coder_prompt = f"/no_think\nTask:\n{prompt}"
    if plan:
        coder_prompt += f"\n\nImplementation brief (reference only, do not quote):\n{plan}"
    if file_content:
        coder_prompt += (
            f"\n\nExisting file ({file}):\n```\n{file_content}\n```\n"
            "Return the complete updated file only."
        )

    is_file_op = bool(file and mode in ("edit", "patch"))
    system_msg = (
        "You are a precise code editor. Return the complete updated file only. No explanation, no markdown fences."
        if is_file_op else
        "You are a code generator. Return complete working code only. No explanation."
    )

    # Step 3 — coder generates
    code = ""
    try:
        code = _code([
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": coder_prompt},
        ], max_tokens, 0.1)
        # Strip stray markdown fences if model wraps output
        if code.startswith("```"):
            lines = code.splitlines()
            code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    except Exception as e:
        print(f"[gen] coder step failed: {e}", file=sys.stderr)

    # Write back for edit/patch
    written = False
    if is_file_op and code:
        Path(file).write_text(code, encoding="utf-8")
        written = True
        print(f"[gen] wrote {file}", file=sys.stderr)

    return {"plan": plan, "code": code, "written": written, "file": file}


def main():
    parser = argparse.ArgumentParser(description="Two-model adviser→coder gen pipeline")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--edit",  metavar="FILE", help="Edit an existing file in place")
    group.add_argument("--patch", metavar="FILE", help="Patch an existing file in place")
    group.add_argument("--gen",   action="store_true", help="Plain generation (default)")
    parser.add_argument("--local", action="store_true",
                        help="Load models in-process via llama-cpp-python (default: HTTP server)")
    parser.add_argument("prompt", nargs="+", help="Task description")
    args = parser.parse_args()

    prompt  = " ".join(args.prompt)
    backend = "local" if args.local else "http"
    if args.edit:
        result = gen(prompt, file=args.edit,  mode="edit",  backend=backend)
    elif args.patch:
        result = gen(prompt, file=args.patch, mode="patch", backend=backend)
    else:
        result = gen(prompt, mode="gen", backend=backend)

    print("\n=== PLAN ===")
    print(result["plan"] or "(none)")
    print("\n=== CODE ===")
    print(result["code"] or "(none)")
    if result["written"]:
        print(f"\n[written → {result['file']}]")


if __name__ == "__main__":
    main()
