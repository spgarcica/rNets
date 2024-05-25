import sys
from pathlib import Path

from rnets import parser as pr
from rnets import plotter as pt


def generate(cf: Path, rf: Path) -> str:
    nw = pr.parse_network_from_file(cf, rf)
    dot = str(pt.thermo.build_dotgraph(nw))

    if cf.stem.endswith("simple") or rf.stem.endswith("simple"):
        return "\n".join(
            (
                dot.rsplit("\n", 1)[0],  # dot minus last line
                '{rank = same; "[A+N+W+W]"; "[A+N+N+W]"};'
                '{rank = same; "[I+N+W+W]"; "[I+W+W+W]"};'
                '{rank = same; "[H+W+W]"; "[H+N+W]"};'
                '{rank = same; "[I+N+W]"; "[I+W+W]";"[I+W]"};'
                '{rank = same; "N"; "[N+W]"; "W"};'
                "}",
            )
        )

    return dot


if __name__ == "__main__":
    cf, rf, of = map(Path, sys.argv[1:])
    of.write_text(generate(cf, rf), encoding="utf-8")
