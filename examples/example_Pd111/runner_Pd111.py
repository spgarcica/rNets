import subprocess

import sys

from itertools import chain, starmap

from rnets import parser as pr
from rnets import plotter as pt
from rnets import struct as st
from rnets.addons.colorbar import ColorbarCfg



comp = sys.argv[1]
rx = sys.argv[2]


if __name__ == "__main__":
    nw = pr.parse_network_from_file(comp, rx)
    nw_test = pt.thermo.build_dotgraph(nw,colorbar_cfg=ColorbarCfg(anchor="H2(g)"))

    with open("graph.dot", 'w', encoding="utf8") as of:
        of.write(str(nw_test))
