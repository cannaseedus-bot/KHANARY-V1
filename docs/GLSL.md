# GLSL.md — OpenGL 4.3 Compute Path (universal GPU target)

GLSL is the **universal GPU compute target** — it runs on every GPU since ~2012
(Intel iGPU, AMD, NVIDIA, mobile) via the installed ICD (`ig75icd64.dll` on the
HD 4600), with **no hardware purchase**. It sits alongside the two other GPU
paths on this rig:

| Path | API | Shader | Hardware | Status |
|------|-----|--------|----------|--------|
| **D3D11_1** | Direct3D 11.1 | HLSL `cs_5_0` (DXBC) | HD 4600 (FL11.x) | ✅ native (`d3d11_infer.dll`) |
| **Direct3D** | D3D12 | HLSL `cs_6_0` (DXIL) | needs FL12+ | ⚠️ HD 4600 can't (FL11.x) |
| **GLSL** | OpenGL 4.3 | GLSL compute | any GPU since 2012 | ✅ universal (`gl_infer_driver`, `GLSL_server`) |

## Why GLSL
- The HD 4600 is **FL11.x** — it cannot run D3D12/DXIL (SM6) shaders.
- Shaders that use **SM6 wave intrinsics** (`WaveGetLaneCount`, `WaveActiveSum`,
  `WavePrefixCountBits`) are D3D12-only and must be **converted to GLSL** to run
  on this hardware.
- GLSL compute (`GL_ARB_compute_shader` + SSBO) gives the same primitives as
  CUDA/D3D11 for inference: matmul, reductions, elementwise ops.

## HLSL → GLSL mapping

| HLSL | GLSL |
|------|------|
| `StructuredBuffer<float> A : register(t0)` | `layout(std430, binding=0) readonly buffer A { float a[]; }` |
| `RWStructuredBuffer<float> B : register(u0)` | `layout(std430, binding=1) buffer B { float b[]; }` |
| `[numthreads(16,16,1)]` | `layout(local_size_x=16, local_size_y=16, local_size_z=1) in;` |
| `SV_DispatchThreadID` | `gl_GlobalInvocationID` |
| `SV_GroupThreadID` | `gl_LocalInvocationID` |
| `SV_GroupID` | `gl_WorkGroupID` |
| `groupshared float s[256]` | `shared float s[256];` |
| `GroupMemoryBarrierWithGroupSync()` | `barrier();` |
| `WaveGetLaneCount()` | `gl_SubGroupSize` (GL_KHR_shader_subgroup) or workgroup size |
| `WaveActiveSum(x)` | `subgroupAdd(x)` (GL_KHR_shader_subgroup) or workgroup reduction |
| `WavePrefixCountBits(x)` | `subgroupBallot` + `subgroupBallotExclusiveBitCount` (or workgroup scan) |

> Note: subgroup ops need `GL_KHR_shader_subgroup` (not core in 4.3). For
> portability, prefer **workgroup reductions via `shared` memory + `barrier()`**,
> which are core OpenGL 4.3.

## The shader set

`dist/v3.5.0-WebX/shaders/` — 34 HLSL shaders (MoE/micronaut, GPT-2 training,
K'uhul folds). Compiled to **D3D11 `cs_5_0`** in `cs5/` (28 OK). The two
**D3D12-only** ones (`orchestrate`, `experts`) use SM6 wave intrinsics and are
the GLSL-conversion targets.

## GLSL_server

`GLSL_server.exe` (`.Powernaut-v1.0.0/dist/`) is the OpenGL 4.3 compute server
(KHL REST on `:9060`): `/inference`, `/dispatch`, `/gravity`, `/node`, etc.
It's the runtime that executes GLSL compute shaders on the HD 4600.

## Usage alongside D3D11_1 and Direct3D
- **D3D11_1 `cs_5_0`** — the native path for GPT-2 inference/training
  (`d3d11_infer.dll`, `gpt2_trainer.exe`).
- **Direct3D (D3D12)** — reserved for FL12+ hardware (DXIL/SM6).
- **GLSL** — the universal fallback + the path for the SM6-only shaders
  (orchestrate/experts) converted to work on the HD 4600.

See also: `GPU.md` (provider inventory), `STUDIO.md` (acceleration policy),
`FOLDS.md` (Fold/Node + SCXQDDS).

## micronaut.glsl / micronaut.hlsl — GPU-resident micronaut

The micronaut concept reaches the GPU as a **resident semantic specialist**. The
C# hall monitor decides *which* micronaut may act; the kernel performs the
bounded `S_mu = W·C·R` field scoring + reduction to the dominant/admissible
micronaut. Mirrors GPT-OSS's MoE shape (router field → top-K) but over explicit
semantic capabilities:

```glsl
// micronaut.glsl  (OpenGL 4.3, GLSL_server)
S = weight * confidence * relevance;
if (S >= 0.5) admitted++;
// workgroup reduction -> dominant index
```

- `dist/v3.5.0-WebX/shaders/micronaut.glsl` — OpenGL 4.3 / GLSL_server path.
- `dist/v3.5.0-WebX/shaders/micronaut.hlsl` — D3D11_1 `cs_5_0` mirror
  (`fxc /T cs_5_0 /E main` → `cs5/micronaut.cso`).
