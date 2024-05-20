from collections.abc import Sequence
import importlib.util
import json
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

    return check_module("rnets") and check_exec("dot") and check_exec("neato")


if not check_deps():
    exit(1)

from rnets import parser as pr
from rnets import plotter as pt

assets = Path("assets")
temp = Path("temp")
temp_graphs = temp / "graphs"
result = Path("res")


def intermediate_graphs(arr: Sequence[int]) -> Sequence[Path]:
    def aux(cf: Path, rf: Path, of: Path) -> Path:
        nw = pr.parse_network_from_file(cf, rf)
        graph = pt.kinetic.build_dotgraph(nw)

        of.write_text(str(graph), encoding="utf-8")
        return of

    return [
        aux(
            assets / f"Pd_comp_{i}.csv",
            assets / f"Pd_reac_{i}.csv",
            temp_graphs / f"graph_{i}.dot",
        )
        for i in arr
    ]


def sh(*args: str) -> None:
    print(*args)
    subprocess.run(args)
    return


def main() -> None:
    temp.mkdir(exist_ok=True)
    temp_graphs.mkdir(exist_ok=True)
    result.mkdir(exist_ok=True)

    arr = (
        0,
        1000,
        2500,
        5000,
        8000,
        8500,
        9250,
        9350,
        9450,
        9500,
        9650,
        9750,
        10000,
        10250,
        11914,
    )

    graph_paths = intermediate_graphs(arr)
    base_graph = assets / "base_graph.dot"
    props = temp / "props.json"

    sh("dot", "-Tpng", str(base_graph), "-o", "auto_layout_orig.png")

    with open(base_graph, "r", encoding="utf-8") as f:
        content = list(
            filter(
                lambda t: t[1].strip().count('"') >= 2 and t[1].strip()[-1] == "[",
                enumerate(f.readlines()),
            )
        )

    nodes = [
        (i, line.replace('"', "").replace("[", "").strip())
        for i, line in content
        if "->" not in line
    ]
    edges = [
        (i, line.replace('"', "").replace("[", "").strip())
        for i, line in content
        if "->" in line
    ]

    sh("dot", "-Tjson", str(base_graph), "-o", str(props))
    with open(props, "r") as f:
        data = json.load(f)

    nodes_data, edges_data = data["objects"], data["edges"]
    pos_info = {item["name"]: item["pos"] for item in nodes_data}

    edge_mapping = {}
    for ed in edges_data:
        pos = ed["pos"]
        head, tail = ed["head"], ed["tail"]
        start = nodes_data[int(head)]["name"]
        end = nodes_data[int(tail)]["name"]
        edge_mapping[f"{start} -> {end}"] = pos
        edge_mapping[f"{end} -> {start}"] = pos

    for n, g in enumerate(graph_paths):
        gs = g.read_text().split("\n")

        for i, node in nodes:
            gs[i] += f' pos="{pos_info[node]}!",'

        for i, node in edges:
            gs[i] += f' pos="{edge_mapping[node]}",'

        gr = g.with_stem(f"{g.stem}_nw")
        r = result / f"{n}.png"

        gr.write_text("\n".join(gs))

        sh("neato", "-n2", "-Tpng", str(gr), "-o", str(r))
    return


if __name__ == "__main__":
    main()
