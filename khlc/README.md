# KHLC — K'UHUL Semantic Compiler

**GitHub:** https://github.com/cannaseedus-bot/KHLC-PY
**KXC (kernel compiler):** https://github.com/cannaseedus-bot/KXC
**SMCA registry:** https://github.com/cannaseedus-bot/SMCA

Compiles `.kuhul` semantic programs and `.khl` driver contracts into KAST + KSON.

```powershell
python tools/khlc.py stdlib/pi.kuhul    # → pi.kson
python tools/kson_validate.py pi.kson   # ADMITTED / REJECTED
```

---

## Why does it look like this?

```kuhul
⟁ Pop ⟁
  bind π = 3.141592653589793
  probe geometry

⟁ Sek ⟁
  dispatch provider(area)

⟁ Xul ⟁
  commit result
```

The `⟁` is a triangle. Not decorative — load-bearing.

A triangle is the minimum closed polygon and the GPU's irreducible primitive. Every
mesh in D3D11 is triangles. Every compute dispatch starts from triangle topology.
A fold has three minimum elements: enter (`Pop`), body, exit (`Xul`). The delimiter
is a triangle because **the container it marks is geometrically triangular** — a
bounded region with a defined entry and exit on a manifold.

The phase names (`Pop`, `Wo`, `Yax`, `Sek`, `Ch'en`, `Xul`) are not decoration
either. They are the six faces of the K-Cube — a 6-face semantic tensor
`[6, 1024, 1024, 4]` where each face corresponds to one phase of the execution
cycle. The fold engine is a geometric state machine, not a keyword system.

The glyphs (`bind`, `probe`, `dispatch`, `commit`) map directly to GPU opcodes:

| Glyph verb | Opcode | What it does |
|------------|--------|--------------|
| `bind` | BIND | establish a value in the geometric field |
| `probe` | PROBE | sense provider availability |
| `resolve` | RESOLVE | select the execution path |
| `dispatch` | DISPATCH | fire a compute shader |
| `collect_status` | COLLECT | read result back |
| `commit` | COMMIT | collapse state — lowest-entropy arc wins |

This maps exactly onto the DirectWrite rendering pipeline:
token → glyph index → GPU geometry → pixels. KHLC compiles programs that run on
the same D3D11 silicon that renders text. The syntax looks like it does because
**it is the hardware's own geometry**, expressed as source.

---

## Two source surfaces

**Semantic modules** (`.kuhul`) — what a program wants:

```kuhul
⟁ Pop ⟁
  bind π = 3.141592653589793
  probe geometry

⟁ Wo ⟁
  bind radius = 8
  bind area = π * radius * radius

⟁ Yax ⟁
  resolve provider = geometry.compute

⟁ Sek ⟁
  dispatch provider(area)

⟁ Ch'en ⟁
  collect_status result

⟁ Xul ⟁
  commit result
```

**Driver contracts** (`.khl`) — how a capability attaches to hardware:

```khl
glyph opengl::dispatch(TENSOR_IN) →
  gl::upload(TENSOR_IN)        → GPU_BUF
  gl::bind_shader("compute")   → PROG
  gl::dispatch(GPU_BUF, PROG)  → OUT_BUF
  yield OUT_BUF
```

Both compile to the same IR: KAST (`protocol: kast/1`) serialized as KSON.

---

## Usage

```powershell
# compile one file
python tools/khlc.py stdlib/pi.kuhul

# compile a directory
python tools/khlc.py --compile-dir stdlib/

# admission gate
python tools/kson_validate.py pi.kson

# tamper test — must REJECT
python tools/kson_validate.py --tamper pi.kson
```

## Reference program

`examples/stdlib/pi.kuhul` exercises all 6 phase folds. Compiled node sequence:

```
n1  Pop    BIND     π = 3.141592653589793
n2  Pop    PROBE    geometry
n3  Wo     BIND     radius = 8
n4  Wo     BIND     area = π * radius * radius
n5  Yax    RESOLVE  provider = geometry.compute
n6  Sek    DISPATCH provider(area)
n7  Ch'en  COLLECT  result
n8  Xul    COMMIT   result
```

## For compute shader kernels

See **KXC**: https://github.com/cannaseedus-bot/KXC

KXC compiles `.kuhul` kernel descriptors → HLSL / WGSL / SMCA JSON.
KHLC compiles `.kuhul` / `.khl` semantic programs → KAST / KSON.
Same language, different compiler, different output domain.

## Contents

```
tools/
  khlc.py             compiler (KHL → KAST → KSON)
  kson_validate.py    admission gate
examples/
  stdlib/
    core.kuhul
    constants.kuhul
    pi.kuhul           reference conformance program
  drivers/
    fold.khl
    inference.khl
VERSION.json
README.md
```
