from collections.abc import Sequence
import importlib.util
import shutil
import sys
from pathlib import Path
import subprocess


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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

def check_deps() -> bool:
    return (
        check_module("rnets")
        and check_module("numpy")
        and check_module("scipy")
        and check_exec("dot")
        and (check_exec("magick") or check_exec("convert")) # magick, version >= 7; convert version <= 6
    )


if not check_deps():
    exit(1)

from rnets import parser as pr
from rnets import plotter as pt

import kinetic_model
import kinetic_snapshot
import kinetic_gif

assets = Path("assets")
temp = Path("temp")
result = Path("res")
temp.mkdir(exist_ok=True)
result.mkdir(exist_ok=True)
model_path = assets / "kinetic_model.data"


def sh(*args: str) -> None:
    print(*args)
    subprocess.run(args)
    return


def main() -> None:
    model = kinetic_model.generate(model_path)
    if model is None:
        exit(1)

    snapshots = kinetic_snapshot.generate(
        assets / "comps_draco_42_simple.csv",
        assets / "reactions_draco_42_simple.csv",
        model,
        temp,
    )

    for snapshot, of in zip(snapshots, ("figure_7a.png", "figure_7b.png")):
        sh("dot", "-Tpng", str(snapshot), "-o", str(result / of))

    snapshots = kinetic_snapshot.generate(
        assets / "comps_draco_42.csv",
        assets / "reactions_draco_42.csv",
        model,
        temp,
    )

    for snapshot, of in zip(snapshots, ("figure_S5.png", "figure_S6.png")):
        sh("dot", "-Tpng", str(snapshot), "-o", str(result / of))

    snapshots = kinetic_gif.generate(
        assets / "comps_draco_42.csv", assets / "reactions_draco_42.csv", model, temp
    )

    def aux(snapshot):
        png = str(snapshot.with_suffix(".png"))
        sh("dot", "-Tpng", str(snapshot), "-o", png)
        return png

    pngs = [aux(snapshot) for snapshot in snapshots]

    if check_exec("magick"):
        sh(
            "magick",
            "convert",
            "-delay",
            "0",
            "-loop",
            "1",
            *pngs,
            str(result / "imine_graph_animation.gif"),
        )
    else:
        sh(
            "convert",
            "-delay",
            "0",
            "-loop",
            "1",
            *pngs,
            str(result / "imine_graph_animation.gif"),
        )


if __name__ == "__main__":
    main()
