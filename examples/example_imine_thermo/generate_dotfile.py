import sys

from rnets import parser
from rnets import plotter
from rnets.plotter.utils import NodeCfg, GraphCfg

compounds_file = sys.argv[1]
reactions_file = sys.argv[2]
output_file = sys.argv[3] 

if __name__ == "__main__":
    nw = parser.parse_network_from_file(compounds_file, reactions_file)
    nw_as_dot = str(plotter.thermo.build_dotgraph(nw))
    
    if compounds_file.endswith('simple.csv') or reactions_file.endswith('simple.csv'): 
        _txt = nw_as_dot.rsplit('\n',1)[0] # remove last line
        _txt += '\n'
        _txt += '{rank = same; "[A+N+W+W]"; "[A+N+N+W]"};\n'
        _txt += '{rank = same; "[I+N+W+W]"; "[I+W+W+W]"};\n'
        _txt += '{rank = same; "[H+W+W]"; "[H+N+W]"};\n'
        _txt += '{rank = same; "[I+N+W]"; "[I+W+W]";"[I+W]"};\n'
        _txt += '{rank = same; "N"; "[N+W]"; "W"};\n'
        _txt += '}\n'
        nw_as_dot = _txt

    with open(output_file, 'w', encoding="utf8") as of:
        of.write(nw_as_dot)
