"""Tests for euler_tour_tree.core.EulerTourTree."""

import unittest

from euler_tour_tree import EulerTourTree


class TestEulerTourTree(unittest.TestCase):
    def test_singleton_connectivity(self):
        t = EulerTourTree()
        self.assertTrue(t.connected("a", "a"))
        self.assertFalse(t.connected("a", "b"))

    def test_add_vertex_is_idempotent(self):
        t = EulerTourTree()
        t.add_vertex("a")
        t.add_vertex("a")
        self.assertTrue(t.connected("a", "a"))
        self.assertFalse(t.connected("a", "b"))

    def test_link_connects(self):
        t = EulerTourTree()
        t.link("a", "b")
        self.assertTrue(t.connected("a", "b"))
        self.assertTrue(t.connected("b", "a"))

    def test_link_cycle_raises(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.link("b", "c")
        with self.assertRaises(ValueError):
            t.link("a", "c")

    def test_link_self_raises(self):
        t = EulerTourTree()
        with self.assertRaises(ValueError):
            t.link("a", "a")

    def test_cut_disconnects(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.cut("a", "b")
        self.assertFalse(t.connected("a", "b"))

    def test_cut_missing_edge_raises(self):
        t = EulerTourTree()
        t.add_vertex("a")
        t.add_vertex("b")
        with self.assertRaises(ValueError):
            t.cut("a", "b")

    def test_cut_twice_raises(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.cut("a", "b")
        with self.assertRaises(ValueError):
            t.cut("a", "b")

    def test_vertices_yields_all(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.link("b", "c")
        self.assertEqual(set(t.vertices()), {"a", "b", "c"})

    def test_edges_yields_ordered_pairs(self):
        t = EulerTourTree()
        t.link("b", "a")
        self.assertEqual(list(t.edges()), [("a", "b")])

    def test_edges_after_cut(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.link("b", "c")
        t.cut("a", "b")
        self.assertEqual(list(t.edges()), [("b", "c")])

    def test_components_after_cut(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.link("b", "c")
        t.cut("b", "c")
        self.assertTrue(t.connected("a", "b"))
        self.assertFalse(t.connected("a", "c"))
        self.assertFalse(t.connected("b", "c"))

    def test_cut_in_middle_of_path(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.link("b", "c")
        t.link("c", "d")
        t.cut("b", "c")
        self.assertTrue(t.connected("a", "b"))
        self.assertFalse(t.connected("a", "c"))
        self.assertTrue(t.connected("c", "d"))

    def test_vertices_after_cut(self):
        t = EulerTourTree()
        t.link("a", "b")
        t.cut("a", "b")
        self.assertEqual(set(t.vertices()), {"a", "b"})

    def test_edges_empty(self):
        t = EulerTourTree()
        self.assertEqual(list(t.edges()), [])

    def test_connected_unknown_vertices(self):
        t = EulerTourTree()
        self.assertFalse(t.connected("x", "y"))
        self.assertTrue(t.connected("x", "x"))


if __name__ == "__main__":
    unittest.main()
