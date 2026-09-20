# KHΛNARY V1
<img src="https://github.com/cannaseedus-bot/KHANARY/raw/main/khanary.png">
**Multi-alphabet Semantic Encoding and Execution Substrate for Deterministic Neural Compute Pipelines**

KHANARY encodes tensor operations and control flow into 32-bit **Knowledge Numeric Unit** (KNU) words using the `KHΛ-2-DENSE-32` profile, enabling deterministic replay of neural compute workloads on CPU with optional iGPU acceleration via WebGPU / GLSL / HLSL.

---

## What's in this repo

| Directory | Contents |
|-----------|----------|
| `models/` | Birdsong geometry model (STB format, KNU encoding, HLSL/WGSL kernels) |
| `docs/` | STB format spec, birdsong geometry grammar, tensor fields, brain schema |
| `tools/` | STB read/write, brain→STB, GGUF→STB, safetensors→STB converters |
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
