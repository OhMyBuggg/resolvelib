def _recursive_check_cyclic(edges, key, visited):
    """Walk a graph to check if an edge set is cyclic.

    The method is fairly naive: If the key has been visited, this must be
    cyclic. Otherwise walk one step in each direction, and see if any of them
    are visited.
    """
    if key in visited:
        return True
    visited.add(key)
    try:
        targets = edges[key]
    except KeyError:
        return False
    return any(
        _recursive_check_cyclic(edges, target, visited)
        for target in targets
    )


class GraphAcyclicError(ValueError):
    pass


class DirectedAcyclicGraph(object):

    def __init__(self):
        self.vertices = {}  # <key> -> Any
        self.edges = {}     # <key> -> Set[<key>]

    def __iter__(self):
        return iter(self.vertices)

    def __len__(self):
        return len(self.vertices)

    def __contains__(self, key):
        return key in self.vertices

    def __getitem__(self, key):
        return self.vertices[key]

    def __eq__(self, other):
        return (
            self.vertices == other.vertices and
            self.edges == other.edges
        )

    def add_vertex(self, key, value):
        self.vertices[key] = value

    def add_edge(self, from_key, to_key):
        # Make sure both ends are in the graph.
        for v in (from_key, to_key):
            if v not in self.vertices:
                raise KeyError(v)

        # We're good if this edge already exists.
        if from_key in self.edges and to_key in self.edges[from_key]:
            return

        # Make sure this new edge won't make the graph cyclic.
        if _recursive_check_cyclic(self.edges, to_key, {from_key}):
            raise GraphAcyclicError(from_key, to_key)

        # Add the edge.
        if from_key not in self.edges:
            self.edges[from_key] = {to_key}
        else:
            self.edges[from_key].add(to_key)