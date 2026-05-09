from app.runners.graph import _topo_order, _parents_of


def test_topo_linear():
    nodes = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    edges = [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}]
    assert _topo_order(nodes, edges) == ["a", "b", "c"]


def test_topo_diamond_multi_parent():
    nodes = [{"id": "a"}, {"id": "b"}, {"id": "c"}, {"id": "d"}]
    edges = [
        {"source": "a", "target": "b"},
        {"source": "a", "target": "c"},
        {"source": "b", "target": "d"},
        {"source": "c", "target": "d"},
    ]
    order = _topo_order(nodes, edges)
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")


def test_topo_falls_back_on_cycle():
    nodes = [{"id": "a"}, {"id": "b"}]
    edges = [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}]
    out = _topo_order(nodes, edges)
    assert set(out) == {"a", "b"}


def test_parents_multi():
    edges = [
        {"source": "a", "target": "c"},
        {"source": "b", "target": "c"},
        {"source": "c", "target": "d"},
    ]
    assert sorted(_parents_of("c", edges)) == ["a", "b"]
    assert _parents_of("a", edges) == []
