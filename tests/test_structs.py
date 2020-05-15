import pytest

from resolvelib.structs import DirectedGraph


@pytest.fixture()
def graph():
    return DirectedGraph()


def test_simple(graph):
    """
    a -> b -> c
    |         ^
    +---------+
    """
    graph.add("a")
    graph.add("b")
    graph.add("c")
    graph.connect("a", "b")
    graph.connect("b", "c")
    graph.connect("a", "c")
    assert set(graph) == {"a", "b", "c"}
    assert set(graph.iter_edges()) == {("a", "b"), ("a", "c"), ("b", "c")}

    """
    a -> b -> c  d
    |         ^
    +------------+
    """
    graph.add("d")
    assert graph.connected("b", "c") is True
    assert graph.connected("b", "d") is False

    with pytest.raises(ValueError) as ctx:
        graph.add("d")
    assert str(ctx.value) == "vertex exists"

    assert set(graph.iter_children("a")) == {"b", "c"}
    assert set(graph.iter_parents("b")) == {"a"}