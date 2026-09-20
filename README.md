# KHΛNARY V1
<img src="https://github.com/cannaseedus-bot/KHANARY/raw/main/khanary.png">
**Multi-alphabet Semantic Encoding and Execution Substrate for Deterministic Neural Compute Pipelines**

KHANARY encodes tensor operations and control flow into 32-bit **Knowledge Numeric Unit** (KNU) words using the `KHΛ-2-DENSE-32` profile, enabling deterministic replay of neural compute workloads on CPU with optional iGPU acceleration via WebGPU / GLSL / HLSL.

---

## What's in this repo

| Directory | Contents |
|-----------|----------|
| `models/` | Birdsong geometry model (STB format, KNU encoding, HLSL/WGSL kernels) |
| `docs/` | STB format spec, birdsong geometry grammar, tensor fields, brain schema; GPU compute stack ([GPU.md](docs/GPU.md), [GLSL.md](docs/GLSL.md), [PHASE-TRANSFORMER.md](docs/PHASE-TRANSFORMER.md)) |
| `tools/` | STB read/write, brain→STB, GGUF→STB, safetensors→STB converters; `gen.py` / `gen.mjs` two-model adviser→coder pipeline |
| `grammar/` | `KHANARY.EBNF` — unified K'UHUL grammar v7.0.0 (1496 lines, 23 sections); sub-grammars: kast, kfold, khl-rom, kxml, xcfe, xjson, xshard, pi-enforcement, KLSL shader PEG; ebnf-parser + grammar-validator tooling |
| `klsl/` | KLSL kernel sources — the K'UHUL shader IR (`.kuhul` → HLSL / WGSL / GLSL) |
| `kxc/` | KXC compiler v1 — `.kuhul` kernel descriptor → HLSL / WGSL / SMCA JSON / CPU C++ |
| `khlc/` | KHLC compiler v1 — `.kuhul` / `.khl` semantic source → KAST / KSON |
| `kxml/` | KXML inference graph format — declarative compute graphs + chat templates |
| `stdlib/` | K'UHUL standard library — `.kuhul` + compiled `.kson` (core, geometry, glsl, hlsl, gravity, physics, …) |

---

## Core concepts

### STB model format
The `.stb` (Semantic Tensor Binary) format encodes neural model weights alongside a KAST semantic graph. Every tensor node carries `fold`, `opcode`, `gravity`, and `symbol` — the geometry is part of the model, not an afterthought. See `docs/stb-format.md`.

### Birdsong geometry
The birdsong mesh (`models/khanary-geometry-v0.3.0/data/birdsong_mesh.stb`) is the canonical reference geometry: a 2MB self-contained model encoding the brain lattice topology. It is the ground truth for KNU vertex transforms and the KLSL trigbrain lattice. See `docs/BIRDSONG_GEOMETRY.md`.

### KNU encoding (KHΛ-2-DENSE-32)
32-bit Knowledge Numeric Unit words encode tensor ops and control flow for deterministic replay. Vertex skin/transform kernels in `models/khanary-geometry-v0.3.0/knu/` define the encoding spec.

### KLSL — one IR, three shader targets
```
.kuhul kernel source
    ↓ KXC
KLSL IR
    ├── emit_hlsl  → D3D11 cs_5_0  (Windows iGPU)
    ├── emit_wgsl  → WebGPU/WGSL   (browser/cross-platform)
    └── emit_glsl  → OpenGL 4.3    (universal — every GPU since 2012)
```

### GPU compute stack
Three confirmed GPU paths for iGPU inference (Intel HD 4600 and equivalents):

| Path | Mechanism | Used by |
|------|-----------|---------|
| `llama-server` HTTP | WebGPU/Dawn (`ggml-webgpu.dll`) | `gen.py` default, `gen.mjs --http` |
| Python local | `torch-directml` (DirectML via D3D12) | `gen.py --local` |
| Node local | `node-llama-cpp` + WebGL2 | `gen.mjs` default |

Full stack documentation: [`docs/GPU.md`](docs/GPU.md) — covers D3D11 cs_5_0, DirectML/KLSL forward pass, OpenCL, XVM 32-fiber cluster, fold tensor system, skeleton/bone routing, and hybrid trainer architecture. [`docs/GLSL.md`](docs/GLSL.md) — OpenGL 4.3 universal compute path. [`docs/PHASE-TRANSFORMER.md`](docs/PHASE-TRANSFORMER.md) — phase-addressed field architecture.

### KXML
Declarative inference graph format with tool-aware Jinja chat templates. One KXML front-end drives any GGUF model through the stock-model adapter. KXML is the topology layer — it describes the compute graph; `.kuhul` / `.khl` own the application logic; C++ / C# / PS1 nodes in KXML are strictly system I/O boundary hooks (`@effect: io`, `@effect: process`). See `kxml/README.md`.

### K'UHUL grammar
`grammar/KHANARY.EBNF` is the canonical 23-section unified grammar (v7.0.0). It covers the full language surface: lexical structure, geometric operators, tensor definitions, compression folds, manifold execution, ECMAScript agent model, micronauts, MoE routing, KXML topology, policy engine, entanglement, and the compression universe container. Sub-grammars in `grammar/` cover KAST, KFOLD, KHL-ROM, XCFE, XJSON, XSHARD, the π enforcement layer, and the KLSL shader PEG. Parse with `grammar/ebnf-parser.js`; validate with `grammar/grammar-validator.js`.

**Language split:**
- `.kuhul` / `.khl` — application logic, kernels, training loops, agents (90%+ of a KHANARY app)
- `KLSL` — math lowering layer (`.kuhul` → HLSL / WGSL / GLSL), stays in `klsl/`
- `KXML` — graph topology, orchestration stubs only
- C++ / C# / PS1 — system boundary only; no application logic

---

## gen.py — adviser→coder pipeline

`tools/gen.py` is a two-model generation pipeline: an adviser model (Gemma 3 1B) produces a 5–8 bullet implementation brief, then a coder model (Qwen3 1.7B) generates code using the brief as context.

Both `tools/gen.py` (Python) and `tools/gen.mjs` (Node.js) implement the same pipeline. The Node version uses `node-llama-cpp` with WebGL2 as the default GPU backend; use `--http` to switch to the llama-server.

```bash
# Node — WebGL2 GPU (default)
npm install
node tools/gen.mjs "build a dark mode toggle"
node tools/gen.mjs --edit path/to/file.html "add a search bar"
node tools/gen.mjs --http "task"          # switch to HTTP server

# Python — HTTP server (default) or llama-cpp-python --local
python tools/gen.py "build a dark mode toggle"

# Edit an existing file in place
python tools/gen.py --edit path/to/file.html "add a search bar to the header"

# Patch an existing file in place
python tools/gen.py --patch path/to/file.js "replace hardcoded port 8080 with process.env.PORT"

# Use local llama-cpp-python backend instead of HTTP server
python tools/gen.py --local "landing page for GPU inference toolkit"
```

Or import as a module:
```python
from tools.gen import gen
result = gen("add error handling", file="server.js", mode="edit")
# returns: {"plan": ..., "code": ..., "written": bool, "file": ...}
```

Configure via environment variables:
| Variable | Default |
|----------|---------|
| `KHANARY_INFER_URL` | `http://127.0.0.1:9000/v1/chat/completions` |
| `KHANARY_ADVISER_MODEL` | `E:\models\GEMMA\gemma-3-1b-Q4_K_M.gguf` |
| `KHANARY_CODER_MODEL` | `C:\Users\canna\.lmstudio\models\...\Qwen3-1.7B-Q8_0.gguf` |

The HTTP backend (`--http`, default) expects a running `llama-server` on port 9000. The local backend (`--local`) loads GGUFs in-process via `llama-cpp-python`.

---

## Convert a model to STB

```bash
# From GGUF
python tools/gguf_to_stb.py model.gguf model.stb

# From safetensors
python tools/safetensors_to_stb.py model.safetensors model.stb

# Verify birdsong geometry
python tools/check_birdsong.py models/khanary-geometry-v0.3.0/data/birdsong_mesh.stb
```

## Compile a kernel

```bash
# .kuhul → HLSL + WGSL + SMCA
kxc/bin/kxc.exe klsl/forward.kuhul --emit hlsl,wgsl,smca

# .kuhul → KAST/KSON
python khlc/tools/khlc.py klsl/forward.kuhul
```

---

## SCXQ7 containers

SCXQ7 quantized expert shards are **not included** — they are built from HuggingFace datasets or via distillation from tracks/brain patterns. See the main KHANARY repo for the distillation pipeline. This repo provides the format spec and geometry starters; SCXQ7 tooling builds on top of them.

---

## License

Proprietary — © canna.seed.us. Contact maintainer for usage terms.
