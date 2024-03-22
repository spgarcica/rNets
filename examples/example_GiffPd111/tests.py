import sys

from itertools import chain, starmap

from rnets import parser as pr
from rnets import plotter as pt
from rnets import struct as st

comp = sys.argv[1]
rx = sys.argv[2]

flag = sys.argv[3]

viridis_colors = [
    [0.267004, 0.004874, 0.329415],
    [0.282623, 0.140926, 0.457517],
    [0.253935, 0.265254, 0.529983],
    [0.206756, 0.371758, 0.553117],
    [0.163625, 0.471133, 0.558148],
    [0.127568, 0.566949, 0.550556],
    [0.134692, 0.658636, 0.517649],
    [0.266941, 0.748751, 0.440573],
    [0.477504, 0.821444, 0.318195],
    [0.741388, 0.873449, 0.149561],
    [0.993248, 0.906157, 0.143936]]


if __name__ == "__main__":
    nw = pr.parse_network_from_file(comp, rx)
    if flag == "kin":
        nw_test = pt.kinetic.build_dotgraph(nw)
    else:
        nw_test = pt.thermo.build_dotgraph(nw)
    
    with open("graph.dot", 'w', encoding="utf8") as of:
        of.write(str(nw_test))
