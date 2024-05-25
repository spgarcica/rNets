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

    return check_module("rnets") and check_exec("dot")


if not check_deps():
    exit(1)

from rnets import parser as pr
from rnets import plotter as pt

import dotfile

assets = Path("assets")
temp = Path("temp")
temp.mkdir(exist_ok=True)
result = Path("res")
result.mkdir(exist_ok=True)


def sh(*args: str) -> None:
    print(*args)
    subprocess.run(args)
    return


def dots(figures: Sequence[tuple[Path, Path, Path]]) -> Sequence[Path]:
    def aux(f, cf, rf):
        f.write_text(dotfile.generate(cf, rf), encoding="utf-8")
        return f

    return [aux(f, cf, rf) for f, cf, rf in figures]


def main() -> None:
    figures = (
        (
            temp / "figure_3a",
            assets / "comps_paper_simple.csv",
            assets / "reactions_paper_simple.csv",
        ),
        (
            temp / "figure_3b",
            assets / "comps_32_simple.csv",
            assets / "reactions_32_simple.csv",
        ),
        (
            temp / "figure_S3",
            assets / "comps_paper.csv",
            assets / "reactions_paper.csv",
        ),
        (
            temp / "figure_S4",
            assets / "comps_32.csv",
            assets / "reactions_32.csv",
        ),
    )

    d = dots(figures)

    for i in d:
        sh(
            "dot",
            "-Tpng",
            str(i),
            "-o",
            str(result / i.with_suffix(".png").name),
        )

if __name__ == "__main__":
    main()
