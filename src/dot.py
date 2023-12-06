"Write a reaction network in dot format"


from typing import Dict, NamedTuple, Sequence
from enum import auto, StrEnum


IDENT = 4


class OptKind(StrEnum):
    "Enum representing the possible kind of global `Opts` values"
    Graph = auto()
    Node = auto()
    Edge = auto()


class Opts(dict):
    """Newtype representing the possible options for nodes, edges and graph

    Attributes:
        options (dict of str keys and str values): Dictionary containing the options.
    """
    def __str__(self): return opts_to_str(self)


class Node(NamedTuple):
    """Structure representing a dot graph node.

    Attributes:
        name (str): Name of the node.
        options (`Opts`): dot options for the node.
    """
    name: str
    options: Opts | None = None

    def __str__(self): return node_to_str(self)


class Edge(NamedTuple):
    """Structure representing a dot edge between two nodes.

    Attributes:
        start (str): Starting node name.
        target (str): Target node name.
        direction (str): Symbol to use to connect both nodes.
            See dot manual for possible values.
        options (`Opts`): Options of the edge.
    """
    origin: str
    target: str
    direction: str = "->"
    options: Opts | None = None

    def __str__(self): return edge_to_str(self)


class Graph(NamedTuple):
    """Structure representing a dot graph.

    Attributes:
        kind (str): Graph type.
        nodes (sequence of `Node`): Nodes in the graph.
        edges (sequence of `Edge`): Edges in the graph.
        options(dict of `OptKind` as keys and `Opt` as values):
            Dictionary containing multiple global options.
    """
    kind: str
    nodes: Sequence[Node]
    edges: Sequence[Edge]
    options: Dict[OptKind, Opts] | None

    HEADER = "strict {}"

    def __str__(self): return graph_to_str(self)


def ident(
    s: str
    , i: int
    , first: bool = True
) -> str:
    """Ident the given string.

    Args:
        s (str): String that will be idented.
        i (int): Identation level.
        first (bool, optional): Wether or not ident the first line.
            defaults to True

    Returns:
        str idented string.

    Note:
        This is not the optimal way to perform the identation as we should
        build new string every time that we ident. However, I think that it
        is more useful than to put the identation during the writing.
    """
    return (" " * first * i) + s.replace('\n', '\n' + ' ' * i)


def ident_if(
    s: str | None
    , i: int
    , first: bool = True
) -> str:
    """Same as `ident` but returns an empty string if the input string is
    empty or None.

    Args:
        s (str or None): String that will be idented.
        i (int): Identation level.
        first (bool, optional): Wether or not ident the first line.
            defaults to True.

    Returns:
        str of the idented string or an empty string.
    """
    if not s:
        return ""
    return ident(s, i, first)


def graph_to_str(
    g: Graph
) -> str:
    """Converts a `Graph` into a dot string.

    Args:
        g (`Graph`): Graph that will be converted.

    Returns:
        str of the dot format.
    """
    if not g.options: return ""
    os = '\n'.join(
        map(
            lambda xs: opts_glob_to_str(*xs) + ';'
            , g.options.items()
        )
    )

    return (
        g.HEADER.format(g.kind) + "{"
        + "\n\n" + ident(os, IDENT, True) + "\n\n"
        + "\n\n".join(map(
            lambda x: ident_if("\n".join(map(str, x)), IDENT, True)
            , (g.nodes, g.edges)))
        + "\n}"
    )


def opts_to_str(
    o: Opts
) -> str:
    """Converts a `Opts` into a string.

    Args:
        n (`Opts`): Opts that will be converted.

    Returns:
        str of the dot format
    """
    out = ',\n '.join(('='.join(o) for o in o.items()))
    return f"[{out}]"


def edge_to_str(
    e: Edge
) -> str:
    """Converts a `Edge` into a string.

    Args:
        n (`Edge`): Edge that will be converted.

    Returns:
        str of the dot format
    """
    spc = len(e.origin) + len(e.direction) + len(e.target)
    return (
        f'"{e.origin}"'
        + ' ' + e.direction
        + ' ' + f'"{e.target}"'
        + ident_if(
            None if e.options is None else (' ' * IDENT + opts_to_str(e.options))
            , (spc + IDENT + 3)
            , False
        ) + ';'
    )


def node_to_str(
    n: Node
) -> str:
    """Converts a `Node` into a string

    Args:
        n (`Node`): Node that will be converted.

    Returns:
        str of the dot format
    """
    return (
        f'"{n.name}"'
        + (' ' * IDENT)
        + ident_if(
            None if n.options is None else opts_to_str(n.options)
            , len(n.name) + IDENT
            , False
        ) + ';'
    )


def opts_glob_to_str(
    k: OptKind
    , o: Opts
) -> str:
    """Format a name followed by `Opts`. Used to define global variables.

    Args:
        k (`OptKind`): `OptKind` for which the global options will be decided.
        o (`Opts`): Global options to define.

    Returns:
        str of the dot format.
    """
    return (
        k + ' ' \
        + ident(
            opts_to_str(o)
            , len(k) + 2
            , False
        )
    )
