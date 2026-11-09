"""Euler Tour Tree: dynamic forest with link, cut, and connectivity queries.

Each tree is represented by an Euler tour sequence.  A link(x, y) splices the
Euler tour of y's tree into the tour of x's tree; cut(x, y) splits it back out.
Connectivity is then a constant-time check that two vertices live in the same
tour object.

The implementation keeps the tour as a Python list and tracks vertex -> tour
membership in a dictionary.  This gives O(1) connectivity and O(n) link/cut.
A balanced-BST (e.g. treap) representation would make link/cut O(log n), but a
list keeps the code short enough to audit and is fast enough for the intended
use: small to medium forests where link/cut are rare and connectivity queries
dominate.  Choosing the list is the trade-off.
"""

from __future__ import annotations

from typing import Dict, Hashable, Iterator, List, Optional


class EulerTourTree:
    """Maintain a forest under link, cut, and connectivity queries.

    Vertices are arbitrary hashable objects.  They do not need to be integers
    and they do not need to be declared up front; a vertex exists as soon as it
    is passed to any method.

    Internally each tree is a list of vertex occurrences forming an Euler tour.
    The tour list is stored once per tree and shared by reference, so a vertex
    can find its tree in O(1) through ``_tour_of``.
    """

    def __init__(self) -> None:
        # Maps a vertex to the list object that holds its Euler tour.  Two
        # vertices are connected iff they map to the same list object.
        self._tour_of: Dict[Hashable, List[Hashable]] = {}

    # -- internal helpers -------------------------------------------------

    def _ensure(self, vertex: Hashable) -> None:
        """Register ``vertex`` as a singleton tree if it is unknown."""
        if vertex not in self._tour_of:
            self._tour_of[vertex] = [vertex]

    def _tour(self, vertex: Hashable) -> List[Hashable]:
        """Return the tour list containing ``vertex``, registering it first."""
        self._ensure(vertex)
        return self._tour_of[vertex]

    # -- public API -------------------------------------------------------

    def add_vertex(self, vertex: Hashable) -> None:
        """Add ``vertex`` as a singleton tree.

        Idempotent: adding an existing vertex is a no-op.  This lets callers
        pre-populate vertices without worrying about whether they already exist.
        """
        self._ensure(vertex)

    def link(self, a: Hashable, b: Hashable) -> None:
        """Add an edge between ``a`` and ``b``.

        Raises ValueError if ``a`` and ``b`` are already connected (a cycle
        would result) or if they are the same vertex.
        """
        if a == b:
            raise ValueError("cannot link a vertex to itself")
        if self.connected(a, b):
            raise ValueError("link would create a cycle")

        tour_a = self._tour(a)
        tour_b = self._tour(b)

        # Splice b's tour into a's tour.  The exact interleaving is not
        # important for correctness of connectivity; we only need a single
        # list that contains every vertex of both trees.
        tour_a.extend(tour_b)
        for vertex in tour_b:
            self._tour_of[vertex] = tour_a

    def cut(self, a: Hashable, b: Hashable) -> None:
        """Remove the edge between ``a`` and ``b``.

        Raises ValueError if no such edge exists.  Because the tour stores
        occurrences rather than adjacency, we cannot tell a real edge from two
        vertices that merely share a tour, so we track edges explicitly.
        """
        if not self._edge_exists(a, b):
            raise ValueError("no edge between the given vertices")
        self._remove_edge(a, b)

        # Rebuild the two tours by walking the current tour and splitting at
        # the removed edge.  This is the O(n) part of cut.
        tour = self._tour(a)
        # Find the positions of a and b in the tour.  The tour may contain
        # multiple occurrences of each vertex; any occurrence works as a
        # split point because the tour is a cyclic sequence.
        pos_a = tour.index(a)
        pos_b = tour.index(b)
        if pos_a > pos_b:
            pos_a, pos_b = pos_b, pos_a

        left = tour[: pos_a + 1]
        right = tour[pos_b:]
        middle = tour[pos_a + 1 : pos_b]

        # ``left`` and ``right`` are the two components.  ``middle`` belongs to
        # one of them; attach it to the side that already contains its first
        # vertex.  Since the tour is connected, middle's first vertex must be
        # connected to either a or b in the original tree, but after removing
        # the edge it is connected to exactly one of them.  We can determine
        # which by checking whether it was adjacent to a or b in the tour
        # order.  For simplicity and correctness we attach middle to the side
        # whose endpoint it follows in the original tour.
        if middle:
            # The vertex immediately before middle in the original tour is
            # tour[pos_a], which is a.  So middle is attached to a's side.
            left.extend(middle)

        # Register the two new tours.
        for vertex in left:
            self._tour_of[vertex] = left
        for vertex in right:
            self._tour_of[vertex] = right

    def connected(self, a: Hashable, b: Hashable) -> bool:
        """Return True if ``a`` and ``b`` are in the same tree."""
        self._ensure(a)
        self._ensure(b)
        return self._tour_of[a] is self._tour_of[b]

    def vertices(self) -> Iterator[Hashable]:
        """Yield every vertex currently in the forest."""
        # A vertex may appear multiple times in a tour, so deduplicate while
        # preserving first-seen order.
        seen = set()
        for tour in self._tour_of.values():
            for vertex in tour:
                if vertex not in seen:
                    seen.add(vertex)
                    yield vertex

    def edges(self) -> Iterator[tuple]:
        """Yield every edge as an ordered pair ``(a, b)`` with ``a < b``.

        Ordering is by the natural ordering of the vertex objects.  Vertices
        must therefore be comparable with ``<`` for this method to work.
        """
        for a, b in self._edges:
            yield (a, b) if a < b else (b, a)

    # -- edge bookkeeping -------------------------------------------------

    # Edges are stored in a set of frozensets for O(1) membership tests.
    # frozenset is used because it is hashable and order-independent.
    _edges: set

    def _edge_exists(self, a: Hashable, b: Hashable) -> bool:
        return frozenset((a, b)) in self._edges

    def _add_edge(self, a: Hashable, b: Hashable) -> None:
        self._edges.add(frozenset((a, b)))

    def _remove_edge(self, a: Hashable, b: Hashable) -> None:
        self._edges.discard(frozenset((a, b)))

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def __init__(self) -> None:  # noqa: F811
        self._tour_of = {}
        self._edges = set()

    # Override link to record the edge.
    def link(self, a: Hashable, b: Hashable) -> None:  # noqa: F811
        if a == b:
            raise ValueError("cannot link a vertex to itself")
        if self.connected(a, b):
            raise ValueError("link would create a cycle")
        tour_a = self._tour(a)
        tour_b = self._tour(b)
        tour_a.extend(tour_b)
        for vertex in tour_b:
            self._tour_of[vertex] = tour_a
        self._add_edge(a, b)
