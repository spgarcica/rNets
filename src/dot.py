"Write a reaction network in dot format"


from collections.abc import Sequence
from itertools import starmap
from typing import NamedTuple
from enum import auto, StrEnum


Opts = dict[str, str]
OptsGlob = dict[str, Opts]
IDENT = 4


class OptKind(StrEnum):
    "Enum representing the possible kind of global :obj:`Opts` values"
    Graph = auto()
    Node = auto()
    Edge = auto()


class Node(NamedTuple):
    """Structure representing a dot graph node.

    Attributes:
        name (str): Name of the node.
        options (:obj:`Opts`): dot options for the node.
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
        options (:obj:`Opts`): Options of the edge.
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
        nodes (sequence of :obj:`Node`): Nodes in the graph.
        edges (sequence of :obj:`Edge`): Edges in the graph.
        options(dict of str as keys and :obj:`Opts` as values):
            Dictionary containing multiple global options.
    """
    kind: str
    nodes: Sequence[Node]
    edges: Sequence[Edge]
    options: OptsGlob | None

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
        str: Idented string.

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
        str: Either the idented string or an empty string.
    """
    if not s:
        return ""
    return ident(s, i, first)


def graph_to_str(
    g: Graph
) -> str:
    """Converts a :obj:`Graph` into a dot string.

    Args:
        g (:obj:`Graph`): Graph that will be converted.

    Returns:
        str: Graph in dot format.
    """
    if not g.options: return ""

    return (
        g.HEADER.format(g.kind) + "{"
        + "\n\n" + ident(opts_glob_to_str(g.options), IDENT, True) + "\n\n"
        + "\n\n".join(map(
            lambda x: ident_if("\n".join(map(str, x)), IDENT, True)
            , (g.nodes, g.edges)))
        + "\n}"
    )


def opts_to_str(
    o: Opts
) -> str:
    """Converts a :obj:`Opts` into a string.

    Args:
        n (:obj:`Opts`): Options that will be converted.

    Returns:
        str: of the dot format
    """
    out = ',\n '.join(('='.join(o) for o in o.items()))
    return f"[{out}]"


def edge_to_str(
    e: Edge
) -> str:
    """Converts a :obj:`Edge` into a string.

    Args:
        n (:obj:`Edge`): Edge that will be converted.

    Returns:
        str: Edge in dot format.
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
    """Converts a :obj:`Node` into a string

    Args:
        n (:obj:`Node`): Node that will be converted.

    Returns:
        str: Node in the dot format.
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


def opt_glob_to_str(
    k: str
    , o: Opts
) -> str:
    """Format a name followed by :obj:`Opts`. Used to define global variables.

    Args:
        k (str): :obj:`OptKind` for which the global options will be decided.
        o (:obj:`Opts`): Global options to define.

    Returns:
        str: Options in dot format.
    """
    return (
        k + ' '
        + ident(
            opts_to_str(o)
            , len(k) + 2
            , False
        )
    )


def opts_glob_to_str(
    os: OptsGlob
) -> str:
    """Format a :obj:`OptsGlob` in dot format.

    Args:
        os (:obj:`OptsGlob`): To convert to dot format.

    Returns:
        str: Global options in dot format.
    """
    return (
        "\n".join(starmap(opt_glob_to_str, os.items()))
    )
