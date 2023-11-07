"Create a pydot object from the given network"


from itertools import repeat, starmap
from typing import Dict, NamedTuple, Sequence
from enum import auto, StrEnum

# from .struct import Network, Direction


GRAPH_ATTR_DEF = {
    'rankdir': 'TB'
    , 'ranksep': '0.5'
    , 'nodesep': '0.5'
}

IDENT = 4

class OptKind(StrEnum):
    Graph = auto()
    Node = auto()
    Edge = auto()


class Opts(NamedTuple):
    options: Dict[str, str]

    def __str__(self):
        return opts_to_str(self)


class Node(NamedTuple):
    name: str
    options: Opts | None = None

    def __str__(self):
        return node_to_str(self)

class Edge(NamedTuple):
    origin: str
    target: str
    direction: str = "->"
    options: Opts | None = None


class Graph(NamedTuple):
    kind: str
    nodes: Sequence[Node]
    edges: Sequence[Edge]
    opts: Dict[OptKind, Opts] | None

    HEADER = "strict {}"

    def __str__(self):
        os = ("{} {};".format(k, ident(str(v), IDENT, False)) for k, v in self.opts.items())
        print("\n\n".join(os))
        return ""

        return self.HEADER.format(self.kind) + "{" \
            + "".join(map(
                lambda x: ident_if("\n\n".join(str(x)), IDENT, True)
                , (os, self.nodes, self.edges))) \
            + "\n}"


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
        str with the idented string or an empty string.
    """
    if not s:
        return ""
    return ident(s, i, first)


def opts_to_str(
    o: Opts
) -> str:
    """Converts a `Opts` into a string.

    Args:
        n (`Opts`): Opts that will be converted.

    Returns:
        str with the dot format
    """
    out = ',\n'.join(('='.join(o) for o in o.options.items()))
    return f"[{out}]"


def edge_to_str(
    e: Edge
) -> str:
    """Converts a `Edge` into a string.

    Args:
        n (`Edge`): Edge that will be converted.

    Returns:
        str with the dot format
    """
    spc = len(e.origin) + len(e.direction) + len(e.target)
    return e.origin \
        + ' ' + e.direction \
        + ' ' + e.target \
        + ident_if(
            (' ' * IDENT) + str(e.options)
            , (spc + IDENT + 3)
            , False
        ) + ';'


def node_to_str(
    n: Node
) -> str:
    """Converts a `Edge` into a string

    Args:
        n (`Node`): Node that will be converted.

    Returns:
        str with the dot format
    """
    return n.name \
        + (' ' * IDENT) \
        + ident_if(
            str(n.options)
            , len(n.name) + IDENT + 1
            , False
        ) + ';'

def opts_glob_to_str(
    k: OptKind
    , o: Opts
) -> str:



# HTML template for compound boxes
BOX_TMP: str = """<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="20">
  <TR>
    <TD BGCOLOR="{0}">{1}</TD>
  </TR>
</TABLE>
>
"""
# HTML template for the compounds text
LABEL_TMP: str = '<FONT COLOR="{0}">{1}</FONT>'


if __name__ == "__main__":
    test_opt = Opts({"color": "red", "sponge": "potato", "shape": "circle"})
    test_nodes = (
        Node("A1", test_opt)
        , Node("A2", test_opt)
        , Node("B1", test_opt)
        , Node("B2", test_opt)
    )

    test_edges = (
        Edge("A1", "A2", "->", test_opt)
        , Edge("A2", "A1", "->", test_opt)
        , Edge("A2", "B1", "->", test_opt)
        , Edge("B1", "B2", "->", test_opt)
    )
    graph_opt = {
        OptKind.Edge: test_opt
        , OptKind.Node: test_opt
        , OptKind.Graph: test_opt
    }

    test_graph = Graph("digraph", test_nodes, test_edges, graph_opt)
