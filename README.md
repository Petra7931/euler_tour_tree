# euler_tour_tree

Maintain a forest under link, cut, and connectivity queries by representing each tree as a sequence of vertices from an Euler tour.

```python
from euler_tour_tree import EulerTourTree

t = EulerTourTree()
t.link("a", "b")
t.link("b", "c")
assert t.connected("a", "c")
t.cut("b", "c")
assert not t.connected("a", "c")
assert t.connected("a", "b")
```

## Why this exists

Dynamic connectivity in a forest is a common primitive: union-find handles
incremental links but cannot cut, and a full dynamic-connectivity structure is
heavy.  An Euler tour tree gives O(1) connectivity and simple link/cut at the
cost of O(n) work per link or cut, because the tour is kept as a Python list.
That trade-off is deliberate: the code stays short, auditable, and free of
third-party dependencies.  If link/cut dominate the workload, replace the list
with a balanced BST and the same interface still applies.

## Edge you will hit

The tour stores vertex occurrences, not adjacency.  Two vertices can share a
tour without being directly linked, so `cut(a, b)` must consult a separate edge
set to decide whether the edge exists.  Calling `cut` on a pair that is
connected but not directly linked raises `ValueError`; it does not silently
split the tree at an arbitrary point.

## API

- `EulerTourTree()` — create an empty forest.
- `add_vertex(v)` — register `v` as a singleton tree.  Idempotent.
- `link(a, b)` — add an edge.  Raises `ValueError` on self-link or cycle.
- `cut(a, b)` — remove an edge.  Raises `ValueError` if no such edge.
- `connected(a, b)` — bool.  Unknown vertices are treated as singletons.
- `vertices()` — iterator over every vertex in the forest.
- `edges()` — iterator over every edge as an ordered pair `(a, b)` with `a < b`.
  Vertices must be comparable with `<` for this method.
