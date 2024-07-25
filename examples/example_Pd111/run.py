from collections.abc import Sequence
import importlib.util
import shutil
import sys
from pathlib import Path
import subprocess


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
        check_module("pandas")
        and check_module("numpy")
        and check_exec("rnets")
        and check_exec("dot")
    )


if not check_deps():
    exit(1)

from rnets import parser as pr
from rnets import plotter as pt
from rnets.addons.colorbar import ColorbarCfg

assets = Path("assets")
temp = Path("temp")
result = Path("res")
temp.mkdir(exist_ok=True)
result.mkdir(exist_ok=True)
model_path = assets / "kinetic_model.data"
comps = temp / "Pd_comp.csv"
reactions = temp / "Pd_reac.csv"
graph = temp / "figure_4.dot"
graph2 = temp / "figure_8.dot"

def sh(*args: str) -> None:
    print(*args)
    subprocess.run(args)
    return

def generate_thermo(cf: Path, rf: Path) -> str:
    nw = pr.parse_network_from_file(cf, rf)
    colorbar_cfg = ColorbarCfg(anchor='CO2(g)')
    dot = str(pt.thermo.build_dotgraph(nw,colorbar_cfg=colorbar_cfg))
    return dot

def generate_kinetic(cf: Path, rf: Path) -> str:
    nw = pr.parse_network_from_file(cf, rf)
    colorbar_cfg = ColorbarCfg(anchor='i15')
    dot = str(pt.kinetic.build_dotgraph(nw,colorbar_cfg=colorbar_cfg))
    return dot


def main() -> None:
    # Generate Figure 4
    sh(
        "python",
        "./parser_visual.py",
        "-outfname_comp",
        str(comps),
        "-outfname_rx",
        str(reactions),
        "-in_comp",
        str(assets / "Pd_g.mkm"),
        "-in_rx",
        str(assets / "rm.mkm"),
        "-in_theta",
        'noc',
    )

    graph.write_text(generate_thermo(comps, reactions), encoding="utf-8")

    sh("dot", "-Tpng", str(graph), "-o", str(result / graph.with_suffix(".png").name))

    # Generate Figure 8
    sh(
        "python",
        "./parser_visual.py",
        "-outfname_comp",
        str(comps),
        "-outfname_rx",
        str(reactions),
        "-in_comp",
        str(assets / "Pd_g.mkm"),
        "-in_rx",
        str(assets / "rm.mkm"),
        "-in_theta",
        str(assets / "theta.csv"),
    )

    graph2.write_text(generate_kinetic(comps, reactions), encoding="utf-8")

    sh("dot", "-Tpng", str(graph2), "-o", str(result / graph2.with_suffix(".png").name))


if __name__ == "__main__":
    main()
