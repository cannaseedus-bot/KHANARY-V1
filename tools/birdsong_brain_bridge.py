#!/usr/bin/env python3
"""
birdsong_brain_bridge.py — Map birdsong brain STB expert clusters -> BrainRouter weights.

Reads a khanary_brain.stb (produced by brain_to_stb.py), computes per-expert centroids
in (time, freq, energy) space, sorts by freq, divides into 9 bands matching BrainRouter's
9 micronaut profiles, then writes brain_router_weights.json for BrainRouter.LoadBrainWeights().

The freq axis of the spectrogram encodes concept abstraction:
  low y-pixel (top of image) = high spectral freq = fast, precise patterns (control/code)
  high y-pixel (bottom)      = low spectral freq  = slow, broad patterns  (narrative/verify)

Usage:
    python tools/birdsong_brain_bridge.py C:/ffmpeg/bin/brain1/khanary_brain.stb
    python tools/birdsong_brain_bridge.py C:/ffmpeg/bin/brain1/khanary_brain.stb --out brain_router_weights.json
    python tools/birdsong_brain_bridge.py --brain1 ... --brain2 ... --merge
"""

import argparse
import json
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from stb import read_stb

# 9 BrainRouter profiles in priority order (matches XCFEBrains.cs RegisterIntents)
PROFILES = [
    {"id": "CM-1", "intent": "control",     "fold": "CONTROL_FOLD"},
    {"id": "MM-1", "intent": "infer",        "fold": "COMPUTE_FOLD"},
    {"id": "VM-1", "intent": "render",       "fold": "UI_FOLD"},
    {"id": "PM-1", "intent": "perceive",     "fold": "DATA_FOLD"},
    {"id": "TM-1", "intent": "schedule",     "fold": "TIME_FOLD"},
    {"id": "SM-1", "intent": "store",        "fold": "STORAGE_FOLD"},
    {"id": "HM-1", "intent": "detect_host",  "fold": "STATE_FOLD"},
    {"id": "XM-1", "intent": "expand",       "fold": "PATTERN_FOLD"},
    {"id": "VM-2", "intent": "verify",       "fold": "META_FOLD"},
]

# freq band boundaries (normalized [0,1]) — low value = top of image = high spectral freq
# Ordered high-freq → low-freq matching profiles above
FREQ_BANDS = [
    (0.00, 0.08),   # CM-1 control     — sharpest ridges, fastest oscillations
    (0.08, 0.18),   # MM-1 infer       — token-level patterns
    (0.18, 0.28),   # VM-1 render      — structured output patterns
    (0.28, 0.40),   # PM-1 perceive    — mid-range attention patterns
    (0.40, 0.52),   # TM-1 schedule    — rhythmic / temporal patterns
    (0.52, 0.65),   # SM-1 store       — background persistence patterns
    (0.65, 0.78),   # HM-1 detect_host — low-freq platform/system patterns
    (0.78, 0.90),   # XM-1 expand      — broad narrative envelope
    (0.90, 1.01),   # VM-2 verify      — sub-bass verification signal
]


def load_brain_stb(path: Path) -> dict:
    tensors = read_stb(str(path))
    return {
        "time":          np.asarray(tensors[0]["array"], dtype=np.float32),
        "freq":          np.asarray(tensors[1]["array"], dtype=np.float32),
        "energy":        np.asarray(tensors[2]["array"], dtype=np.float32),
        "edges":         np.asarray(tensors[3]["array"], dtype=np.int32),
        "csr_index":     np.asarray(tensors[4]["array"], dtype=np.int32),
        "csr_neighbors": np.asarray(tensors[5]["array"], dtype=np.int32),
        "expert_ids":    np.asarray(tensors[6]["array"], dtype=np.int32),
    }


def compute_centroids(brain: dict) -> list[dict]:
    """Compute per-expert centroid in (time, freq, energy) space + cluster stats."""
    expert_ids = brain["expert_ids"]
    k = int(expert_ids.max()) + 1
    centroids = []
    for e in range(k):
        mask = expert_ids == e
        if not mask.any():
            continue
        t = float(brain["time"][mask].mean())
        f = float(brain["freq"][mask].mean())
        en = float(brain["energy"][mask].mean())
        size = int(mask.sum())

        # edge density: edges where both endpoints are in this cluster
        edge_a, edge_b = brain["edges"][:, 0], brain["edges"][:, 1]
        in_cluster = np.isin(edge_a, np.where(mask)[0]) & np.isin(edge_b, np.where(mask)[0])
        edge_count = int(in_cluster.sum())

        centroids.append({
            "expert":      e,
            "time":        t,
            "freq":        f,
            "energy":      en,
            "node_count":  size,
            "edge_count":  edge_count,
        })
    return centroids


def normalize_freq(centroids: list[dict]) -> list[dict]:
    """Normalize freq to [0,1] across all centroids."""
    freqs = [c["freq"] for c in centroids]
    f_min, f_max = min(freqs), max(freqs)
    span = f_max - f_min if f_max > f_min else 1.0
    for c in centroids:
        c["freq_norm"] = (c["freq"] - f_min) / span
    return centroids


def assign_to_profiles(centroids: list[dict]) -> dict:
    """
    Assign expert clusters to profiles by freq_norm band.
    Returns dict: profile_id -> {confidence_prior, energy, node_coverage, cluster_count, experts[]}
    """
    n_profiles = len(PROFILES)
    assignments: dict[str, dict] = {}

    for i, (profile, (lo, hi)) in enumerate(zip(PROFILES, FREQ_BANDS)):
        band_clusters = [c for c in centroids if lo <= c["freq_norm"] < hi]

        if band_clusters:
            # aggregate: mean energy, sum coverage
            agg_energy  = float(np.mean([c["energy"]     for c in band_clusters]))
            agg_nodes   = int(sum(c["node_count"]        for c in band_clusters))
            agg_edges   = int(sum(c["edge_count"]        for c in band_clusters))
            expert_list = [c["expert"]                   for c in band_clusters]
        else:
            # empty band — assign neutral weight
            agg_energy  = 0.5
            agg_nodes   = 0
            agg_edges   = 0
            expert_list = []

        assignments[profile["id"]] = {
            "intent":           profile["intent"],
            "fold":             profile["fold"],
            "cluster_count":    len(band_clusters),
            "experts":          expert_list,
            "node_coverage":    agg_nodes,
            "edge_density":     agg_edges,
            "mean_energy":      agg_energy,
        }

    # Normalize energy across all profiles to confidence_prior in [0.6, 1.4]
    energies = [v["mean_energy"] for v in assignments.values() if v["cluster_count"] > 0]
    if energies:
        e_min, e_max = min(energies), max(energies)
        e_span = e_max - e_min if e_max > e_min else 1.0
        for pid, v in assignments.items():
            if v["cluster_count"] > 0:
                norm = (v["mean_energy"] - e_min) / e_span   # [0, 1]
                v["confidence_prior"] = round(0.6 + norm * 0.8, 4)  # [0.6, 1.4]
            else:
                v["confidence_prior"] = 0.8   # neutral for empty bands
    else:
        for v in assignments.values():
            v["confidence_prior"] = 1.0

    return assignments


def merge_assignments(a1: dict, a2: dict) -> dict:
    """Merge two brain assignments by geometric mean of confidence_prior."""
    merged = {}
    for pid in a1:
        p1 = a1[pid]["confidence_prior"]
        p2 = a2.get(pid, {}).get("confidence_prior", 1.0)
        merged[pid] = {
            **a1[pid],
            "confidence_prior": round(float(np.sqrt(p1 * p2)), 4),
            "brain2_confidence_prior": a2.get(pid, {}).get("confidence_prior", 1.0),
        }
    return merged


def print_assignment_table(assignments: dict, label: str) -> None:
    print(f"\n{label}")
    print(f"  {'Profile':<6}  {'Intent':<12}  {'Clusters':>8}  {'Nodes':>7}  {'Energy':>8}  {'Prior':>7}")
    print(f"  {'-'*6}  {'-'*12}  {'-'*8}  {'-'*7}  {'-'*8}  {'-'*7}")
    for pid, v in assignments.items():
        print(f"  {pid:<6}  {v['intent']:<12}  {v['cluster_count']:>8}  "
              f"{v['node_coverage']:>7}  {v['mean_energy']:>8.4f}  {v['confidence_prior']:>7.4f}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Map birdsong brain -> BrainRouter weights")
    ap.add_argument("stb",      nargs="?", default=r"C:\ffmpeg\bin\brain1\khanary_brain.stb")
    ap.add_argument("--brain2", default=r"C:\ffmpeg\bin\brain2\khanary_brain.stb",
                    help="Optional second brain STB to merge (geometric mean of priors)")
    ap.add_argument("--merge",  action="store_true", help="Merge brain1 + brain2 priors")
    ap.add_argument("--out",    default="",
                    help="Output JSON path (default: beside input STB)")
    args = ap.parse_args()

    stb1_path = Path(args.stb)
    out_path  = Path(args.out) if args.out else stb1_path.parent / "brain_router_weights.json"

    print(f"Loading {stb1_path} ...")
    brain1 = load_brain_stb(stb1_path)
    c1 = normalize_freq(compute_centroids(brain1))
    a1 = assign_to_profiles(c1)
    print_assignment_table(a1, f"brain1 ({len(c1)} experts)")

    assignments = a1

    if args.merge and Path(args.brain2).exists():
        print(f"\nLoading {args.brain2} ...")
        brain2 = load_brain_stb(Path(args.brain2))
        c2 = normalize_freq(compute_centroids(brain2))
        a2 = assign_to_profiles(c2)
        print_assignment_table(a2, f"brain2 ({len(c2)} experts)")
        assignments = merge_assignments(a1, a2)
        print_assignment_table(assignments, "merged (geometric mean)")

    # Build output JSON
    output = {
        "_schema":  "khanary.brain_router_weights.v1",
        "_source":  str(stb1_path),
        "_experts": len(c1),
        "profiles": {
            pid: {
                "confidence_prior": v["confidence_prior"],
                "mean_energy":      v["mean_energy"],
                "node_coverage":    v["node_coverage"],
                "cluster_count":    v["cluster_count"],
                "experts":          v["experts"],
            }
            for pid, v in assignments.items()
        }
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
