"""
Khanary-V1 tool configuration — single source of truth for all tools.

Inference server
----------------
llama-server running on DirectML (iGPU) is the ONLY confirmed working
GPU inference path in this repo. All tools that need LLM inference must
use INFER_URL below — do NOT hard-code another endpoint.

Start the server:
    llama-server --model <gguf> --port 9000 --n-gpu-layers -1

Override any value via environment variable before running a tool:
    $env:KHANARY_INFER_URL = "http://192.168.1.5:9000/v1/chat/completions"
    python tools/gen.py "task"
"""

import os

# ---------------------------------------------------------------------------
# Inference server (DirectML GPU — llama-server)
# ---------------------------------------------------------------------------
INFER_URL = os.environ.get(
    "KHANARY_INFER_URL",
    "http://127.0.0.1:9000/v1/chat/completions",
)

# ---------------------------------------------------------------------------
# Local GGUF model paths (used only with --local / backend="local")
# Override to point at your local GGUF weights.
# ---------------------------------------------------------------------------
ADVISER_MODEL = os.environ.get(
    "KHANARY_ADVISER_MODEL",
    r"E:\models\GEMMA\gemma-3-1b-Q4_K_M.gguf",
)

CODER_MODEL = os.environ.get(
    "KHANARY_CODER_MODEL",
    r"C:\Users\canna\.lmstudio\models\lmstudio-community\Qwen3-1.7B-GGUF\Qwen3-1.7B-Q8_0.gguf",
)
