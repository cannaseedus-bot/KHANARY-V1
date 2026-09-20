#!/usr/bin/env python3
# gguf_to_stb.py — GGUF -> KHANARY .stb (dequant path for T004)
#
# Reads a GGUF model, dequants tensors to float32, writes a KHANARY .stb binary
# plus a sidecar .stb.json manifest (name->id index + original GGUF metadata).
#
# Dequant coverage (matching GGUF block formats used by llama.cpp):
#   F32   -> pass-through (tensor.data is already float32 numpy)
#   F16   -> upcast to F32
#   BF16  -> manual uint16-shift upcast
#   Q8_0  -> block dequant: q[i] * scale_f16  (block=32, stride=34 B)
#   Q4_0  -> block dequant: (nibble-8) * scale_f16  (block=32, stride=18 B)
#   Other -> SKIP + warn (Q4_K/Q5_K require super-block dequant; add as needed)
#
# Usage:
#   python tools/gguf_to_stb.py <in.gguf> <out_basename> [--only name1 name2 ...]
#   -> writes <out_basename>.stb  +  <out_basename>.stb.json
import os, sys, json, struct
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stb import write_stb, read_stb

# gguf pip package (llama.cpp); also accepts project-local gguf-py if pip missing
try:
    from gguf import GGUFReader, GGMLQuantizationType
except ImportError:
    gguf_py = Path(__file__).resolve().parent.parent / "khanary-llama-build" / "llama.cpp" / "gguf-py"
    sys.path.insert(0, str(gguf_py))
    from gguf import GGUFReader, GGMLQuantizationType


# ── dequant helpers (all work from raw bytes via tobytes()) ──────────────────

def _raw_bytes(tensor) -> bytes:
    """Extract tensor bytes regardless of numpy dtype returned by GGUFReader."""
    return bytes(np.asarray(tensor.data).tobytes())


def _bf16_to_f32(raw_bytes: bytes, n: int) -> np.ndarray:
    u16 = np.frombuffer(raw_bytes, dtype=np.uint16, count=n).astype(np.uint32)
    return (u16 << 16).view(np.float32)


def _dequant_q8_0(raw_bytes: bytes, n_elem: int) -> np.ndarray:
    """Q8_0: 34 bytes per block — [2B f16 scale | 32B int8 ints]."""
    BS, STRIDE = 32, 34
    n_blocks = n_elem // BS
    out = np.empty(n_elem, dtype=np.float32)
    for b in range(n_blocks):
        off = b * STRIDE
        scale = struct.unpack_from('<e', raw_bytes, off)[0]   # f16 little-endian
        qs = np.frombuffer(raw_bytes, dtype=np.int8, count=BS, offset=off+2).astype(np.float32)
        out[b*BS:(b+1)*BS] = qs * scale
    return out


def _dequant_q4_0(raw_bytes: bytes, n_elem: int) -> np.ndarray:
    """Q4_0: 18 bytes per block — [2B f16 scale | 16B packed 4-bit ints]."""
    BS, STRIDE = 32, 18
    n_blocks = n_elem // BS
    out = np.empty(n_elem, dtype=np.float32)
    for b in range(n_blocks):
        off = b * STRIDE
        scale = struct.unpack_from('<e', raw_bytes, off)[0]
        nibbles = np.frombuffer(raw_bytes, dtype=np.uint8, count=16, offset=off+2)
        lo = (nibbles & 0x0F).astype(np.int32) - 8
        hi = (nibbles >> 4).astype(np.int32) - 8
        block = np.empty(BS, dtype=np.float32)
        block[0::2] = lo * scale
        block[1::2] = hi * scale
        out[b*BS:(b+1)*BS] = block
    return out


def dequant_tensor(name: str, tensor) -> np.ndarray | None:
    """Dequant a GGUFReader tensor to float32. Returns None if unsupported."""
    shape = tuple(int(d) for d in tensor.shape)
    n = int(np.prod(shape))
    qt = tensor.tensor_type
    data = np.asarray(tensor.data)

    # F32: tensor.data is already a float32 numpy array from GGUFReader
    if qt == GGMLQuantizationType.F32:
        return data.astype(np.float32).reshape(shape)

    # F16: tensor.data is a float16 numpy array
    if qt == GGMLQuantizationType.F16:
        return data.astype(np.float32).reshape(shape)

    # All quantized types: extract raw bytes and dequant manually
    raw = _raw_bytes(tensor)

    if qt == GGMLQuantizationType.BF16:
        return _bf16_to_f32(raw, n).reshape(shape)

    if qt == GGMLQuantizationType.Q8_0:
        return _dequant_q8_0(raw, n).reshape(shape)

    if qt == GGMLQuantizationType.Q4_0:
        return _dequant_q4_0(raw, n).reshape(shape)

    print(f"  SKIP {name}: unsupported type {qt.name} (add super-block dequant for K-quants)")
    return None


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    gguf_path = sys.argv[1]
    out_base  = sys.argv[2]
    only_set  = set()
    if "--only" in sys.argv:
        only_set = set(sys.argv[sys.argv.index("--only")+1:])

    reader = GGUFReader(gguf_path)

    # Build architecture metadata from GGUF fields
    meta = {}
    for k, v in reader.fields.items():
        try:
            parts = v.parts
            val = parts[-1] if parts else None
            meta[k] = str(val) if val is not None else ""
        except Exception:
            pass
    arch = meta.get("general.architecture", "unknown")
    print(f"[read] {os.path.basename(gguf_path)}  arch={arch}  tensors={len(reader.tensors)}")

    # Dequant tensors
    converted, skipped = {}, []
    for tensor in reader.tensors:
        name = tensor.name
        if only_set and name not in only_set:
            continue
        arr = dequant_tensor(name, tensor)
        if arr is None:
            skipped.append(name)
            continue
        converted[name] = arr.astype(np.float32)

    if not converted:
        print(f"[warn] no tensors converted (all skipped or filtered)")
        sys.exit(0)

    print(f"[convert] {len(converted)} tensors -> f32  ({len(skipped)} skipped)")

    # Assign stable ids (sorted name order)
    names = sorted(converted.keys())
    name2id = {n: i for i, n in enumerate(names)}

    # Write .stb
    stb_path = out_base + ".stb"
    tensors = [{"tensor_id": name2id[n], "array": converted[n]} for n in names]
    write_stb(stb_path, tensors)
    stb_mb = os.path.getsize(stb_path) / (1 << 20)
    print(f"[stb] wrote {stb_path}  ({stb_mb:.1f} MB, {len(tensors)} tensors)")

    # Verify round-trip (spot-check first/mid/last)
    back = read_stb(stb_path)
    spot = [names[0], names[len(names)//2], names[-1]]
    ok = True
    for n in spot:
        tid = name2id[n]
        a, b = np.asarray(back[tid]["array"]), converted[n]
        match = a.shape == b.shape and np.allclose(a.reshape(b.shape), b, atol=1e-6)
        ok = ok and match
        print(f"  {'PASS' if match else 'FAIL'} tid={tid} {n}  {b.shape}")
    print(f"=== {'PASS' if ok else 'FAIL'}: GGUF -> KHANARY .stb round-trip ===")

    # Write manifest
    manifest = {
        "format": "khanary-gguf-stb/v1",
        "source": os.path.basename(gguf_path),
        "arch": arch,
        "stb": {"file": os.path.basename(stb_path), "tensor_count": len(names), "dtype": "float32"},
        "meta": {k: v for k, v in meta.items() if not k.startswith("tokenizer")},
        "tensors": {n: {"id": name2id[n], "dims": list(converted[n].shape), "original_type": None}
                    for n in names},
        "skipped": skipped,
    }
    # Patch original_type from reader
    for tensor in reader.tensors:
        if tensor.name in name2id:
            manifest["tensors"][tensor.name]["original_type"] = tensor.tensor_type.name

    json_path = out_base + ".stb.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[manifest] wrote {json_path}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
