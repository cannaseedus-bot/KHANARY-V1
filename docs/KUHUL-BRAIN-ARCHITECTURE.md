# K'UHUL Brain Architecture — Recursive Cognition Reference

## Brain definition

$$
\boxed{
Brain = G + T + N + R + E + M + P
}
$$

| Symbol | Layer | What it is |
|--------|-------|------------|
| `G` | Graph topology | GraphDB — semantic node/edge structure |
| `T` | Tensor fields | SVG-3D weighted field over graph entities |
| `N` | N-ary relations | n-grams / supagrams — higher-order semantic units |
| `R` | Routing / ARCs | Directed information-propagation transitions |
| `E` | Experts / Micronauts | Executable reasoning agents |
| `M` | Persistent memory | IDB / MX2DB heap + learned weights |
| `P` | Causal provenance | `cause → effect → proof` hash chain |

K'UHUL is not another item stored beside those. K'UHUL is what **moves the Brain through them**:

$$
\boxed{
Brain_n
\xrightarrow[\theta=0\rightarrow2\pi]{K'UHUL}
Brain_{n+1}
}
$$

---

## The four core separations

$$
\boxed{\text{Graph} = \text{what is related}}
$$

$$
\boxed{\text{n-ary gram} = \text{which semantic entities cohere together}}
$$

$$
\boxed{\text{Tensor} = \text{how strongly that configuration matters now}}
$$

$$
\boxed{\text{ARC} = \text{where information may propagate}}
$$

$$
\boxed{\text{Yax} = \text{which configuration/ARC should be considered}}
$$

$$
\boxed{\text{XCFE} = \text{whether that transition is allowed}}
$$

---

## ARC — directed information transition

$$
\boxed{\operatorname{ARC}: X \xrightarrow{Y} Z}
$$

| Field | Meaning |
|-------|---------|
| `X` | Source information node/subgraph |
| `Y` | Predicted directed arc / relation |
| `Z` | Target/resulting information node |
| `W` | Scalar transition weight |
| `T` | SVG-3D tensor field carried by the arc |
| `ΔH` | Entropy change on traversal |
| `θ` | Phase position in K'UHUL cycle |

Full state:

$$
\boxed{
ARC_t = \langle X,\; Y,\; Z,\; W,\; T,\; \Delta H,\; \theta \rangle
}
$$

Traversing the arc changes the information/entropy state:

$$
\boxed{H_Z = H_X + \Delta H(Y)}
$$

Transformation form:

$$
\boxed{Z = T_Y(X), \qquad H_Z = H_X + \Delta H(Y)}
$$

### Declared edge vs. predicted edge

```
DECLARED EDGE (in GraphDB):
X ─────────────► Z
     known

PREDICTED EDGE (candidate, not yet committed):
X - - - - - - ► Z
        Y
```

A predicted edge **must not automatically become a real graph edge**. It passes through:

```
candidate edge Y
      ↓  Yax
      ↓  XCFE
      ↓  Sek
      ↓  Ch'en
confirmed / rejected
```

---

## 2π phase closure — the recursive cycle

$$
\boxed{
Pop(0) \rightarrow
Wo(\pi/3) \rightarrow
Yax(2\pi/3) \rightarrow
Sek(\pi) \rightarrow
Ch'en(4\pi/3) \rightarrow
Xul(5\pi/3) \rightarrow
Pop(2\pi \equiv 0)
}
$$

`Pop'` is not a seventh phase — it is **Pop on the next revolution**:

$$
\boxed{Pop_{n+1} = Pop(\theta_n + 2\pi)}
$$

| Absolute Θ | Normalized θ | Phase |
|-----------|-------------|-------|
| 0 | 0 | Pop₀ |
| π/3 | π/3 | Wo₀ |
| 2π/3 | 2π/3 | Yax₀ |
| π | π | Sek₀ |
| 4π/3 | 4π/3 | Ch'en₀ |
| 5π/3 | 5π/3 | Xul₀ |
| 2π | 0 | Pop₁ |
| 7π/3 | π/3 | Wo₁ |
| … | … | … |

Phase position is the ARC coordinate, not geometry:

$$
\boxed{\text{Graph position} = \text{where the information is}}
$$

$$
\boxed{\text{Phase position }(\theta) = \text{where the reasoning process is}}
$$

$$
\boxed{\text{Entropy }(H) = \text{state/uncertainty of the information}}
$$

$$
\boxed{\text{SVG-3D tensor }(T) = \text{weighted field carried by the transition}}
$$

One complete K'UHUL revolution is one complete **information reasoning cycle**:

$$
\boxed{
(X_n, H_n)
\xrightarrow[\theta:0\rightarrow2\pi]{ARC}
(X_{n+1}, H_{n+1})
}
$$

---

## Phase semantics per stage

```
POP        acquire X
 │
WO         establish H(X) + graph state + tensor contracts
 │
YAX        propose ARC Y: X ────► Z
 │           candidate, not yet committed
 │
XCFE       authorize Y + validate tensor contract
 │
SEK        apply T_Y / propagate ARC
 │
CH'EN      observe Z and ΔH; compare prediction to result
 │
XUL        collapse Z → X_{t+1}; commit evidence to IDB/JROM
 │
 └──────── Z_n → X_{n+1}   (recursive or terminal)
```

Xul produces two possible outcomes:

```
Xulₙ
 │
 ├── sufficient/validated ─────► RETURN
 │
 └── unresolved/new evidence ──► Popₙ₊₁
                                   │
                                   ▼
                              refreshed approach
                              G_n → G_{n+1}
```

---

## Full revolution state

$$
\boxed{
State_n =
\langle G_n,\; T_n,\; Gram_n,\; IDB_n,\; \theta_n \rangle
}
$$

One revolution produces:

$$
State_{n+1} = F(State_n,\; Discovery_n,\; Outcome_n)
$$

Graph update law:

$$
\boxed{G_{n+1} = F(G_n, \Delta G_n)}
$$

---

## n-ary grams — higher-order semantic units

$$
\boxed{\text{Gram} \neq \text{Node}}
$$

An n-ary gram binds multiple semantic nodes into one retrievable relationship:

```
nodes:
    A = "K'UHUL"
    B = "recursive"
    C = "phase"
    D = "loop"

n-ary gram:
    g = (A, B, C, D)    →    joint semantic configuration g(A,B,C,D)
```

Each gram can carry an associated tensor:

$$
T_g = [W_g, C_g, R_g, E_g, \Delta H_g, \ldots]
$$

| Field | Meaning |
|-------|---------|
| `W_g` | Learned history weight |
| `C_g` | Earned confidence |
| `R_g` | Query relevance |
| `E_g` | Evidence/energy |
| `ΔH_g` | Information/entropy consequence |

**The gram supplies semantic structure; the tensor weighs its significance in the current reasoning state.**

$$
\boxed{\textbf{n-ary grams expose higher-order structure in the graph.}}
$$

$$
\boxed{\textbf{SVG-3D tensors weigh that higher-order structure.}}
$$

### Grams are dynamic evidence

$$
G_n \rightarrow grams_n \rightarrow Yax_n
$$

New nodes discovered at Ch'en unfold new possible grams:

$$
grams_{n+1} = \text{Compile/Resolve}(G_{n+1})
$$

```
REVOLUTION 0
    nodes A B C
       ↓
    grams AB, BC, ABC
       ↓
    select ABC → discover D

REVOLUTION 1
    nodes A B C D
       ↓
    grams AB, BC, ABC, BD, CD, BCD, ABCD
       ↓
    newly relevant topology → refreshed reasoning
```

**Grams help the runtime find and bind the graph; they don't become the graph.**

### Current implementation vs. target

`micronaut-v4/` contains the SCXQ7 definition with two n-ary containers and ~850 MB of n-grams and micronaut-grams. This is the original KHA-NARY n-gram corpus. The grams are built from stack/runtime observations **but already carry semantic grounding via AIML pattern matching, XCFE transition contracts, and ELIZA rules** — they are not flat statistical co-occurrence.

The GraphDB target adds a further layer on top:

| | Current (micronaut-v4 SCXQ7) | Target (this architecture) |
|---|---|---|
| Source | Stack traces, runtime info | Same + GraphDB topology |
| Semantic grounding | AIML / XCFE / ELIZA | AIML / XCFE / ELIZA **+ graph node identity** |
| Coherence | Pattern-matched semantic units | Semantic node binding in graph topology |
| Phase-aware | No | Yes — grams sorted into Pop/Wo/Yax/Sek/Ch'en/Xul |
| Dynamic | Static corpus | `grams_{n+1} = Compile/Resolve(G_{n+1})` |

The 850 MB corpus can **answer questions today** via µN-ary RAG. The GraphDB layer promotes those grams from pattern-indexed to **topology-indexed** — grounded in the 30,628-node brain graph rather than only in AIML/ELIZA semantic rules.

---

## TRACKS — semantic reasoning tracks

Tracks are the phase-indexed semantic QA layer that grounds n-ary grams in the K'UHUL reasoning cycle. Two track formats are in active use.

### `.track.xjson` — micronaut semantic tracks

226 tracks in `micronaut-v4/programs/micronauts/semantic/`. Schema:

```json
{
  "@kind": "micronaut.semantic-tracks.v1",
  "micronaut": { "id": "PM-1", "authority": "XCFE", "audit": "JROM" },
  "tracks": [{
    "id": "alice.artificial-intelligence",
    "topic": "artificial-intelligence",
    "confidence": 0.78,
    "folds": [{
      "id":    "qa-N",
      "topic": "question pattern",
      "phase": "Pop",
      "governs": ["token", "token", "..."],
      "nodes": [
        { "id": "q", "kind": "semantic_node", "semantic_role": "INPUT PATTERN" },
        { "id": "a", "kind": "output",        "semantic_role": "response text"  }
      ]
    }]
  }]
}
```

Each fold is a single Q/A pair assigned to a K'UHUL phase. The `governs` field lists the n-gram tokens this fold anchors. The 6-phase cycle repeats across as many folds as the track contains — wrapping back to Pop, establishing recursive semantic coverage.

Phase assignment semantics in a track fold:

| Phase | Role in Q/A fold |
|-------|-----------------|
| Pop | Perceive — first-contact acquisition |
| Wo | Allocate — establish context frame |
| Yax | Condition — topic selector / discriminant |
| Sek | Output — execute response |
| Ch'en | Commit — evidence / observation record |
| Xul | Collapse — close and hand back |

Topic families in the corpus: AIML/AI, alice identity, adam expert, geography, history, humor, literature, philosophy, and ~220 more.

### DGML — directed reasoning graphs

DGML (Directed Graph Markup Language) is the second track format. It encodes reasoning/thinking paths as directed graphs with typed properties:

```xml
<?xml version="1.0" encoding="utf-8"?>
<DirectedGraph xmlns="https://schemas.microsoft.com/vs/2009/dgml">
  <Nodes>
    <Node Id="a" Label="a" Size="10" />
    <Node Id="b" Background="#FF008080" Label="b" />
    <Node Id="c" Label="c" Start="2010-06-10" />
  </Nodes>
  <Links>
    <Link Source="a" Target="b" />
    <Link Source="a" Target="c" />
  </Links>
  <Properties>
    <Property Id="Background" Label="Background" DataType="Brush" />
    <Property Id="Label"      Label="Label"      DataType="String" />
    <Property Id="Size"       DataType="String" />
    <Property Id="Start"      DataType="DateTime" />
  </Properties>
</DirectedGraph>
```

Where `.track.xjson` encodes a linear phase-indexed QA sequence, DGML encodes a **branching topology** — nodes are reasoning states, links are directed transitions, properties carry typed metadata (phase, timestamp, visual encoding, weight). DGML graphs can be arbitrarily deep and wide, giving the system unbounded reasoning track space.

### Tracks in the Brain architecture

Tracks sit at the intersection of **N** (n-ary grams), **E** (micronauts), and **G** (graph topology):

| Layer | What tracks contribute |
|-------|----------------------|
| `N` — n-ary grams | `.track.xjson` `governs` lists supply phase-keyed gram anchors — each fold contributes its token set to the gram index at the assigned phase |
| `E` — micronauts | Each `.track.xjson` is owned by a named micronaut (`PM-1`, etc.); micronauts are the reasoning agents that fire tracks |
| `G` — graph topology | DGML graphs map directly into GraphDB — nodes become semantic identities, links become ARCs |
| `R` — routing / ARCs | DGML links → ARC candidates; `.track.xjson` phase annotations → ARC `θ` coordinate |
| `M` — memory | Track `confidence` and `audit: JROM` fields feed the IDB causal record |

$$
\boxed{\textbf{Tracks = phase-indexed semantic grounding for n-ary grams}}
$$

$$
\boxed{\textbf{DGML = topological expansion of tracks into arbitrarily deep reasoning graphs}}
$$

---

## MX2DB / IDB memory schema

```
n_grams
supagrams
rlhf_traces
agent_state
training_history
tapes

gram_observations
gram_patterns
gram_macros
```

$$
\boxed{Gram = \text{semantic/retrieval evidence}}
$$

$$
\boxed{Observation = \text{what actually occurred}}
$$

$$
\boxed{Pattern = \text{what repeated experience has established}}
$$

$$
\boxed{Macro = \text{a reusable higher-order structure}}
$$

Earned confidence:

$$
C_g = \frac{\text{validated outcomes for }g}{\text{observed uses of }g}
$$

ARC weight update:

$$
W_{arc}^{n+1} = Update(W_{arc}^{n}, Outcome_n)
$$

### IDB causal record (Ch'en → Xul boundary)

```xml
<step>
    <cause hash="..."/>
    <effect hash="..."/>
    <proof hash="..."/>
</step>
```

$$
Cause = X_n \qquad Effect = Z_n \qquad Proof = \text{evidence supporting } X_n \xrightarrow{Y_n} Z_n
$$

$$
\boxed{Z_n \rightarrow X_{n+1}}
$$

The next Pop can query IDB and know **how it arrived there** — prevents the recursive cycle from repeatedly attempting the same failed approach.

---

## SVG-3D — weighted tensor field over graph topology

GraphDB owns **identity and relationships**. SVG-3D owns **numeric state/weights associated with those identities and relationships**.

$$
\boxed{\text{Tensor Field} \neq \text{Graph Topology}}
$$

but they are indexed against the **same semantic identities**.

$$
G = (V, E) \qquad \text{(discrete GraphDB)}
$$

$$
T: V \cup E \rightarrow \text{Tensor} \qquad \text{(SVG-3D field)}
$$

A predicted edge carries a tensor:

$$
\boxed{Y = (X, Z, T_Y)}
$$

SVG-3D encodes the tensor's semantic structure, lanes, transforms, addressing — the physical weight buffer resides in mmap / GPU / CPU / SCXQ2 separately.

### SVG semantic interpretation contract

| SVG property | K'UHUL semantic |
|---|---|
| `<g>` | fold / semantic container |
| `<path>` | transition trajectory |
| `<use>` | reference/reuse |
| `transform` | state transformation |
| `matrix` | transformation algebra |
| path length | cost |
| curvature | uncertainty/change |
| rotation | phase |
| scale | magnitude/weight |

These are **K'UHUL interpretation contracts**, not SVG defaults.

### SVG mesh as n-ary structure

An ordinary graph ARC is binary: $N_i \rightarrow N_j$

A triangle naturally identifies a ternary relationship:

$$
\boxed{(N_i, N_j, N_k)}
$$

The SVG mesh establishes higher-order relational fields beyond binary edges.

---

## Four weight classes — not interchangeable

$$
\boxed{\text{ARC weights} = \text{decision strength}}
$$

$$
\boxed{\text{Embeddings} = \text{semantic evidence}}
$$

$$
\boxed{\text{Learned weights} = \text{accumulated experience}}
$$

$$
\boxed{\text{Matrices/tensors} = \text{actual transformations}}
$$

ARC candidate scoring:

$$
\boxed{
S_i = W_i C_i R_i E_i - \lambda\, Cost_i - \gamma\, \Delta H_i
}
$$

$$
a^* = \arg\max_{a_i \in A(X)} S_i \quad \text{subject to XCFE constraints}
$$

### ARC object schema

```
ARC
│
├── semantic relation
│
├── scalar weights
│     ├── relevance
│     ├── evidence
│     ├── earned confidence
│     └── learned weight
│
├── feature tensor     (embeddings, when useful)
│
├── transform tensor   (matrices / multidimensional weights)
│
├── constraint tensor  (masks / permissions / bounds)
│
└── entropy ΔH
```

---

## Recursive discovery — fold → unfold cycle

$$
\boxed{
\text{Fold}
\rightarrow \text{Discover}
\rightarrow \text{Unfold}
\rightarrow \text{Validate}
\rightarrow \text{Collapse}
\rightarrow \text{Refresh}
\rightarrow \text{Fold}
}
$$

A node may be initially folded:

```
[Microsoft]
```

Sek invokes the appropriate retriever. The returned information unfolds:

```
[Microsoft]
    ├──develops────► [Windows]
    ├──develops────► [Azure]
    └──relationship► [OpenAI]
```

Yax ranks candidate expansions by relevance before unfolding:

```
C  relevance .93  → unfold
D  relevance .08  → remain folded
E  relevance .71  → unfold
```

**Bounded recursive graph expansion**, not an uncontrolled crawler.

```
                    ┌──────── MEMORY / IDB ─────────┐
                    │                               │
                    ▼                               │
POP₀ → WO₀ → YAX₀ → SEK₀ → CH'EN₀ → XUL₀ ────────┘
 │                                      │
Gₙ (known graph)                    ΔGₙ (discoveries)
                                        ▼
                                  unfold new nodes
                                  update known nodes
                                  validate new arcs
                                  reject bad arcs
                                  attach tensors
                                  update weights
                                        │
                                  Gₙ₊₁ = Gₙ ⊕ ΔGₙ
                                        │
                                      POPₙ₊₁
```

Next approach incorporates prior failures and discoveries:

$$
\boxed{
Approach_{n+1} = P(Q,\; G_{n+1},\; H_{n+1},\; JROM_n)
}
$$

---

## XCFE — schema-validated admission

```
Yax proposes ARC
       ↓
XCFE examines requirements
       ↓
IDB schema-registry
       ↓
deterministic validator (SCXQ2, CM-1, SCXQ7, SCX-BSON)
       ↓
accepted / rejected
       ↓
Sek
```

XCFE validation is deterministic, not probabilistic — **the model thinks this looks valid** is not sufficient.

---

## Brain2 layout — three representations of one brain state

```
brain2/
│
├── SEMANTIC / INSPECTION
│   ├── graph.json          (30,628 nodes, 91,863 edges)
│   ├── tensor_nodes.json   ({id, time, freq, energy, h} per node)
│   ├── mesh.svg            (61,239 polygons — n-ary relational field)
│   ├── ridge_curves.svg
│   └── spectrum.png
│
├── EXECUTION / BINARY PROJECTION
│   ├── tensor_header.bin   (contract tying parallel arrays)
│   ├── nodes_time.bin
│   ├── nodes_freq.bin
│   ├── nodes_energy.bin
│   ├── edges.bin
│   ├── csr_index.bin
│   ├── csr_neighbors.bin
│   ├── routing.bin
│   ├── experts.bin
│   └── experts_kuhul.bin
│
└── PACKAGED BRAIN
    ├── brain.brain
    ├── khanary_brain.stb
    └── idb/
```

Node tensor schema (from tensor_nodes.json):

$$
T(N_i) =
\begin{bmatrix}
time_i \\ freq_i \\ energy_i \\ h_i \\ W_i \\ C_i \\ R_i \\ H_i \\ \theta_i
\end{bmatrix}
$$

`W, C, R, H, θ` are the K'UHUL reasoning fields to be added; `time, freq, energy, h` are the existing substrate.

`TensorHeader` contract:

$$
\boxed{
TensorHeader = \langle count,\; shape,\; dtype,\; layout,\; strides,\; fields,\; identity,\; version \rangle
}
$$

**`h` is not confirmed as entropy `H` — may be hash, Hilbert index, or packed spatial identity. Do not equate until the producing code is inspected.**

---

## Architecture summary diagram

```
GraphDB
   │
   ├── Nodes ───────── semantic identities / information
   │
   ├── ARCs ────────── directed binary relations
   │
   └── n-ary grams ─── higher-order semantic relations
              │
              ▼
       µN-ary retrieval
              │
              ▼
             Yax
       W · C · R(Q)
              │
              ▼
            XCFE
              │
              ▼
             Sek
```

Vocabulary summary:

| Object | Role |
|--------|------|
| `GraphDB` | Topology — semantic identity and relationships |
| `ARC` | Directed information/entropy transition |
| `SVG-3D Tensor` | Weighted higher-order field over that topology |
| `n-ary gram` | Higher-order semantic coherence unit |
| `IDB / MX2DB` | Persistent memory + causal provenance |
| `K'UHUL θ` | Recursive phase position |
| `XCFE` | Admission / control law |
| `Embedding` | One optional evidence field inside the system |
