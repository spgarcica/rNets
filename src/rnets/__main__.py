import tomllib
from collections.abc import Iterable, Sequence
from itertools import chain
from pathlib import Path
from typing import Any, Mapping, NamedTuple, NoReturn, TypeAliasType, Unpack

from rnets import chemistry, parser
from rnets import conf_type_checker as conf
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


def color_check(x: Any) -> bool:
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
    assert isinstance(GeneralCfg, conf.NamedTupleProtocol)
    type_modifiers: Mapping[type | TypeAliasType, conf.NamedTupleMemberModifier] = {
        Opts: conf.NamedTupleMemberModifier(
            conf.resolve_type(Opts, type_modifiers={}).check, opts_transform
        ),
        Path: conf.NamedTupleMemberModifier(
            lambda x, **kwargs: isinstance(x, str), lambda x, **kwargs: Path(x)
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

    config_info = conf.named_tuple_info(GeneralCfg, type_modifiers=type_modifiers)
    with open("config.toml", mode="rb") as f:
        config_dict = tomllib.load(f)
    config = conf.recreate_named_tuple(config_info, config_dict)

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
