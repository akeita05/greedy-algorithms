# Cache Eviction Policy Simulator

## Student Information

| Name | UFID |
|------|------|
| Aicha Keita | 66149226 |

---

## Repository Structure

```
greedy-algorithms/
├── src/
│   └── cache_sim.py
├── data/
│   ├── example.in
│   ├── example.out
│   ├── test1.in
│   ├── test2.in
│   ├── test3.in
│   └── lru_adversarial.in
├── tests/
│   └── test_cache.py 
└── README.md
```

---

## Dependencies

- **Python 3.8+** (uses `collections.OrderedDict`, `collections.deque`)
- No third-party libraries required.

---

## How to Compile / Run

Python is interpreted; no compilation step is needed.

### Run the Simulator

```bash
python3 src/cache_sim.py <input_file>
```

**Example:**

```bash
python3 src/cache_sim.py data/example.in
```

**Expected output:**

```
FIFO  : 13
LRU   : 17
OPTFF : 11
```

### Run All Tests

```bash
python3 tests/test_cache.py
```

---

## Input Format

```
k m
r1 r2 r3 ... rm
```

- `k` = cache capacity (integer ≥ 1)
- `m` = number of requests (integer ≥ 1)
- `r1 ... rm` = space-separated integer item IDs

Requests may span multiple lines; the parser splits on any whitespace.

---

## Output Format

```
FIFO  : <number_of_misses>
LRU   : <number_of_misses>
OPTFF : <number_of_misses>
```

---

## Reproducing Example Output

```bash
git clone https://github.com/akeita05/greedy-algorithms.git
cd cache-eviction
python3 src/cache_sim.py data/example.in
```

Output should match `data/example.out` exactly.

---

## Assumptions

- Item IDs are non-negative integers.
- `k ≥ 1` and `m ≥ 1`.
- Requests need not fit within the cache (i.e., distinct items may exceed `k`).
- The OPTFF implementation runs in O(m · k) per eviction decision; for very large inputs, this is adequate for correctness, though an O(m log k) variant using heaps is possible.

---

---

# Written Component

---

## Question 1: Empirical Comparison

The simulator was run on four input files. Results:

| Input File | k | m  | FIFO | LRU | OPTFF |
|------------|---|----|------|-----|-------|
| example.in | 3 | 20 | 13   | 17  | 11    |
| test1.in   | 3 | 60 | 44   | 44  | 31    |
| test2.in   | 4 | 70 | 60   | 60  | 34    |
| test3.in   | 5 | 80 | 64   | 64  | 36    |

### Commentary

**Does OPTFF have the fewest misses?**  
Yes. In every test case, OPTFF achieves strictly fewer misses than both FIFO and LRU. This is expected: OPTFF is the offline optimal algorithm, so no algorithm can do better on any fixed sequence.

**How does FIFO compare to LRU?**  
On the three larger test files (test1–test3), FIFO and LRU tie. This happens because those sequences use a cycling access pattern over a working set larger than the cache; both policies end up evicting a useful item on every miss. On the `example.in` sequence (which has irregular temporal locality), LRU actually performs *worse* than FIFO (17 vs. 13 misses). This illustrates an important point: LRU's recency heuristic can backfire when the access pattern does not exhibit strong temporal locality. Repeatedly touching an item "protects" it under LRU even if it is not needed soon, while FIFO would have evicted it long ago. Neither policy dominates the other in general.

---

## Question 2: Bad Sequence for LRU (k = 3)

There **does** exist a request sequence for which OPTFF incurs strictly fewer misses than LRU. The following sequence demonstrates this for k = 3:

```
Sequence: 1  2  3  1  4  2  3  1  4  2  3  1  4
k = 3, m = 13
```

Run with:

```bash
python3 src/cache_sim.py data/lru_adversarial.in
```

**Results:**

| Policy | Misses |
|--------|--------|
| FIFO   | 8      |
| LRU    | **12** |
| OPTFF  | **6**  |

### Why LRU Performs Poorly Here

Step through what LRU does:

1. **Requests 1, 2, 3** → 3 misses. Cache: `{1, 2, 3}`.
2. **Request 1** → hit. Cache (by recency): `[2, 3, 1]` (1 is now MRU).
3. **Request 4** → miss. LRU evicts `2` (least recently used). Cache: `{3, 1, 4}`.
4. **Request 2** → miss. LRU evicts `3`. Cache: `{1, 4, 2}`.
5. **Request 3** → miss. LRU evicts `1`. Cache: `{4, 2, 3}`.
6. **Request 1** → miss. LRU evicts `4`. Cache: `{2, 3, 1}`.

Steps 3–6 repeat as a cycle: every time item `4` (which only appears once per cycle) displaces a frequently-requested item. LRU treats `4` as "recently used" and keeps it, evicting `2`, `3`, or `1` instead — each of which is needed in the very next few steps.

**OPTFF** knows `4` will not be needed again until position 8 (or 12), so it evicts `4` instead of a soon-to-be-requested item, reducing misses to 6.

**FIFO** is not fooled by recency either, giving only 8 misses. Still worse than OPTFF but far better than LRU on this sequence.

---

## Question 3: Proof That OPTFF Is Optimal

**Theorem.** Let OPT denote the OPTFF algorithm (Belady's Farthest-in-Future) and let A be *any* deterministic or randomized offline algorithm that knows the full request sequence. Then for every request sequence σ and every cache capacity k,

$$\text{MISSES}_{\text{OPT}}(\sigma) \;\leq\; \text{MISSES}_{A}(\sigma).$$

**Proof (Exchange Argument).**

We show that OPTFF can be transformed into any other algorithm, step-by-step, without decreasing the number of misses, which implies OPTFF's miss count cannot exceed A's.

**Setup.** Fix the request sequence $\sigma = r_1, r_2, \ldots, r_m$ and cache capacity $k$. Consider any offline algorithm A. We will construct a sequence of modified algorithms $A = A_0, A_1, A_2, \ldots$ where each $A_i$ differs from OPTFF in at most the cache states *after* the first $i$ misses, and $\text{MISSES}(A_i) \leq \text{MISSES}(A_{i-1})$. At the end, $A_m = \text{OPT}$.

**Invariant.** After processing request $r_t$, define the *discrepancy* between algorithm X and OPTFF as the set of items in X's cache that are not in OPTFF's cache (and vice versa). We will maintain the invariant that the discrepancy never forces extra misses.

**Key Lemma.** Suppose at some point OPT and A have the same cache state up to (but not including) a particular miss. On that miss for item $p$:
- OPT evicts the item $q$ whose next request is *farthest* in the future (call that position $t_q$).
- A evicts some item $q'$ with next use at position $t_{q'} \leq t_q$.

We modify A into A', which evicts $q$ instead of $q'$ on this miss. We claim A' has no more misses than A:

- Between now and position $t_{q'}$ (the next request for $q'$): A' holds $q'$ in cache and lacks $q$. But A originally lacked $q'$ and held $q$. Any request for $q$ before $t_{q'}$ is a miss for A, but a hit for A'; any request for $q'$ is a hit for A but a miss for A'. However, since $t_{q'} \leq t_q$, item $q'$ is requested no later than $q$. We can "swap" the roles of $q$ and $q'$ in A's cache to match A' without increasing total misses — the first discrepancy request is for $q'$ (a miss for A'), which was a hit for A, but at that point A' can re-insert $q'$ and the cache states become identical again. The net change in misses is **zero**.
- After position $t_{q'}$, A and A' have identical cache states.

Thus MISSES(A') ≤ MISSES(A).

**Completing the Proof.** Starting from A, apply the above exchange at every miss where A's eviction choice disagrees with OPTFF's. Each exchange:
1. Makes one more eviction decision agree with OPTFF.
2. Does not increase the total miss count.

After at most $m$ such exchanges, the algorithm is identical to OPTFF. Since each step is non-increasing in misses,

$$\text{MISSES}_{\text{OPT}} \;\leq\; \text{MISSES}_{A}.$$

Because A was an arbitrary offline algorithm, OPTFF is **optimal** — no algorithm (online or offline) can achieve fewer cache misses on any fixed request sequence. $\blacksquare$

---

*End of Written Component*
