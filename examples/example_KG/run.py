from collections.abc import Sequence, Callable
import importlib.util
import json
import shutil
import sys
from pathlib import Path
import subprocess
from typing import Any


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def check_deps() -> bool:
    def check_module(module: str) -> bool:
        m = importlib.util.find_spec(module)
        if m is None:
            eprint(f"Can't find python module {module}")
            return False
        return True

    def check_exec(executable: str) -> bool:
        e = shutil.which(executable)
        if e is None:
            eprint(f"Can't find executable {executable} in PATH")
            return False
        return True

    return (
        check_module("numpy")
        and check_module("rdflib")
        and check_module("owlready2")
        and check_exec("rnets")
        and check_exec("dot")
    )


if not check_deps():
    exit(1)

from rnets import parser as pr
from rnets import plotter as pt
from rnets.addons.colorbar import ColorbarCfg

import RNets_KG_Parser as kg

temp = Path("temp")
temp_graphs = temp / "graphs"
result = Path("res")
temp.mkdir(exist_ok=True)
result.mkdir(exist_ok=True)
comps = temp / "comps.csv"
reactions = temp / "reactions.csv"
graph = temp / "CycOct_network.dot"
hgraph = graph.with_stem(graph.stem + "_horizontal")


def sh(*args: str) -> None:
    print(*args)
    subprocess.run(args)
    return

def generate(cf: Path, rf: Path) -> str:
    nw = pr.parse_network_from_file(cf, rf)
    colorbar_cfg = ColorbarCfg(anchor='BAK')
    dot = str(pt.thermo.build_dotgraph(nw,colorbar_cfg=colorbar_cfg))
    return dot

def main():
    ref = "EpOr+CO2+TMABr"
    hs = ("CO2", "TMA", "TMABr")

    kq_handler = kg.read_kg_and_query("CycOct.owl")
    compounds, edges = kg.build_rnet_files(kq_handler, ref, hs)

    comps.write_text(compounds, encoding="utf-8")
    reactions.write_text(edges, encoding="utf-8")

    graph.write_text(generate(comps, reactions), encoding="utf-8")
    sh("dot", "-Tpng", str(graph), "-o", str(result / graph.with_suffix(".png").name))
    sh(
        "dot", 
        "-Tpng", str(graph),
        "-Grankdir=LR",
        "-Nfontsize=16",
        "-Granksep=0.1", 
        "-Gnodesep=0.5",
        "-o", str(result / hgraph.with_suffix(".png").name))


if __name__ == "__main__":
    main()
