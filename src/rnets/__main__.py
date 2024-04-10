import argparse
import collections
import tomllib
from collections.abc import Iterable, Sequence
from itertools import chain
from pathlib import Path
from typing import Any, NamedTuple, NoReturn, Self, Unpack

from rnets import chemistry
from rnets import conf_type_checker as conf
from rnets import parser
from rnets.colors import colorschemes, palettes
from rnets.colors import utils as col_utils
from rnets.dot import Opts
from rnets.plotter import kinetic, thermo
from rnets.plotter import utils as pt_utils


def error(exception: Exception | None = None) -> NoReturn:
    raise exception or ValueError()


class GeneralCfg(NamedTuple):
    comp_file: Path
    reac_file: Path
    out_file: Path
    graph: pt_utils.GraphCfg
    chem: chemistry.ChemCfg


def parse_opt(x: str) -> tuple[str, str] | None:
    match x.split("=", 1):
        case key, value:
            return key, value
        case _:
            return None


def parse_opts(xs: Iterable[str]) -> Opts:
    return dict(filter(None, map(parse_opt, xs)))


class OptsAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is None:
            raise ValueError("nargs must not be None")

        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(
        self: Self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        _ = parser, option_string
        if values is None:
            return

        setattr(namespace, self.dest, parse_opts(values))


def chem_group(parser: argparse.ArgumentParser) -> None:
    chem = parser.add_argument_group(
        "Chemistry",  # description=""
    )
    chem.add_argument(
        "-T",
        "--temperature",
        type=float,
        help="Temperature value in K",
        dest="chem.T",
        default=argparse.SUPPRESS,
    )
    chem.add_argument(
        "-u",
        "--units",
        type=str,
        help="Energy units. Used to select kb and A if not provided",
        dest="chem.e_units",
        choices=tuple(chemistry.CONSTANTS['kb'].keys()),
        default=argparse.SUPPRESS,
    )
    chem.add_argument(
        "-kb",
        "--boltzmann",
        type=float,
        help="Boltzmann constant. Overrides the default",
        dest="chem.kb",
        default=argparse.SUPPRESS,
    )
    chem.add_argument(
        "-A",
        "--preexp",
        type=float,
        help="Eyring equation pre-exponetial factor. Overrides the default",
        dest="chem.A",
        default=argparse.SUPPRESS,
    )


def graph_group(parser: argparse.ArgumentParser) -> None:
    graph = parser.add_argument_group(
        "Graph configuration",  # description=""
    )
    graph.add_argument(
        "-k",
        "--kind",
        type=str,
        help="Kind of dotgraph",
        dest="graph.kind",
        default=argparse.SUPPRESS,
    )
    graph.add_argument(
        "-c",
        "--colorscheme",
        type=str,
        help="Color scheme",
        dest="graph.colorscheme",
        choices=tuple(colorschemes.available.keys()),
        default=argparse.SUPPRESS,
    )
    graph.add_argument(
        "-off",
        "--offset",
        nargs=2,
        type=float,
        help="Colorscheme offset",
        dest="graph.color_offset",
        default=argparse.SUPPRESS,
    )
    graph.add_argument(
        "-go",
        "--graph_opts",
        nargs="+",
        help="Graphviz options for graph in dictionary format",
        dest="graph.opts",
        action=OptsAction,
        default=argparse.SUPPRESS,
    )


def edge_group(parser: argparse.ArgumentParser) -> None:
    edge = parser.add_argument_group(
        "Edge configuration",  # description=
    )
    edge.add_argument(
        "-w",
        "--width",
        type=int,
        help="Edge constant/minimum width",
        dest="graph.edge.width",
        default=argparse.SUPPRESS,
    )
    edge.add_argument(
        "-mw",
        "--maxwidth",
        type=int,
        help="Edge maximum width",
        dest="graph.edge.max_width",
        default=argparse.SUPPRESS,
    )
    edge.add_argument(
        "-eo",
        "--edge-opts",
        nargs="+",
        help="Graphviz options for edges in dictionary format",
        dest="graph.edge.opts",
        action=OptsAction,
        default=argparse.SUPPRESS,
    )


def node_group(parser: argparse.ArgumentParser) -> None:
    node = parser.add_argument_group(
        "Node configuration",  # description=
    )
    node.add_argument(
        "-f",
        "--fontcolor",
        type=str,
        help="Font color of the nodes",
        dest="graph.node.font_color",
        default=argparse.SUPPRESS,
    )
    node.add_argument(
        "-a",
        "--fontcoloralt",
        type=str,
        help="Alternate font color of the nodes",
        dest="graph.node.font_color_alt",
        default=argparse.SUPPRESS,
    )
    node.add_argument(
        "-l",
        "--lumthreshold",
        type=float,
        help="Luminance threshold for the nodes",
        dest="graph.node.font_lum_threshold",
        default=argparse.SUPPRESS,
    )
    node.add_argument(
        "-no",
        "--node-opts",
        nargs="+",
        help="Graphviz options for nodes in dictionary format",
        dest="graph.node.opts",
        action=OptsAction,
        default=argparse.SUPPRESS,
    )


def cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="rNets, create a dotfile.")

    parser.add_argument(
        "-cf",
        "--compfile",
        type=Path,
        help="Compounds file",
        dest="comp_file",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-rf",
        "--reacfile",
        type=Path,
        help="Reactions file",
        dest="reac_file",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=str,
        help="Output file name",
        dest="out_file",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-cfg",
        "--config",
        type=str,
        help="Configuration file name",
        default=argparse.SUPPRESS,
    )

    chem_group(parser)
    graph_group(parser)
    edge_group(parser)
    node_group(parser)

    return parser


def parse_cli_args() -> dict[str, Any]:
    return vars(cli_parser().parse_args())


def unflatten_args(args):
    def defdict():
        return collections.defaultdict(defdict)

    res = collections.defaultdict(defdict)
    for k, v in args.items():
        a = res
        *body, tail = k.split(".")
        for i in body:
            a = a[i]
        a[tail] = v
    return res


def merge_configs(cli, config):
    result = cli.copy()

    for key, value in config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def color_check(x: Any) -> bool:
    # TODO: make better check
    return isinstance(x, str)


def color_transform(
    x: str, **kwargs: Unpack[conf.NamedTupleMemberModifierKwargs]
) -> col_utils.Color:
    return (
        palettes.css.get(x)
        or col_utils.hexstr_to_rgb(x)
        or error(ValueError(f"couldn't parse {type(x)}"))
    )


def colorsequence_check(
    x: Any, **kwargs: Unpack[conf.NamedTupleMemberModifierKwargs]
) -> bool:
    return (
        isinstance(x, list)
        and all(color_check(i) for i in x)
        or isinstance(x, str)
        and x.lower() in colorschemes.available
    )


def colorsequence_transform(
    x: list[str] | str, **kwargs: Unpack[conf.NamedTupleMemberModifierKwargs]
) -> Sequence[col_utils.Color]:
    _ = kwargs
    match x:
        case [*colors]:
            return [
                palettes.css.get(color)
                or col_utils.hexstr_to_rgb(color)
                or error(ValueError(f"couldn't parse {color}"))
                for color in colors
            ]
        case str() if x.lower() in colorschemes.available:
            return colorschemes.available[x.lower()]
        case _:
            error()


def opts_transform(
    x: Any, **kwargs: Unpack[conf.NamedTupleMemberModifierKwargs]
) -> Opts:
    return (kwargs.get("default") or {}) | x


def run() -> None:
    type_modifiers: conf.TypeModifiersDict = {
        Opts: conf.NamedTupleMemberModifier(
            conf.resolve_type(Opts, type_modifiers={}).check, opts_transform
        ),
        Path: conf.NamedTupleMemberModifier(
            lambda x, **kwargs: isinstance(x, (str, Path)), lambda x, **kwargs: Path(x)
        ),
        tuple: conf.NamedTupleMemberModifier(
            lambda x, **kwargs: isinstance(x, Iterable), lambda x, **kwargs: tuple(x)
        ),
        col_utils.Color: conf.NamedTupleMemberModifier(
            lambda x, **kwargs: isinstance(x, str),
            color_transform,
        ),
        colorschemes.Colorscheme: conf.NamedTupleMemberModifier(
            colorsequence_check, colorsequence_transform
        ),
    }

    cli_dict = parse_cli_args()
    cfg_path = cli_dict.pop("config", None) or Path(
        "./config.toml"  # TODO: make it constant
    )
    cli_dict = unflatten_args(cli_dict)

    if cfg_path.exists():
        with open(cfg_path, mode="rb") as f:
            config_dict = tomllib.load(f)
    else:
        config_dict = {}

    config_info = conf.named_tuple_info(GeneralCfg, type_modifiers=type_modifiers)
    config = conf.recreate_named_tuple(
        config_info, merge_configs(cli_dict, config_dict)
    )

    network = parser.parse_network_from_file(config.comp_file, config.reac_file)
    # TODO: Extract it to GeneralCfg instead
    plot_thermo = any(
        map(
            lambda x: x is None,
            chain(
                map(lambda x: x.conc, network.compounds),
                map(lambda x: x.energy, network.reactions),
            ),
        ),
    )

    if plot_thermo:
        dot = thermo.build_dotgraph(network, config.graph)
    else:
        dot = kinetic.build_dotgraph(network, config.graph, config.chem)

    with open(config.out_file, "w", encoding="utf8") as out_file:
        out_file.write(str(dot))


if __name__ == "__main__":
    run()
