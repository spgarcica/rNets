import sys
from pathlib import Path

import numpy as np

from rnets import parser
from rnets.struct import Network, Compound, Reaction
from rnets.plotter.kinetic import build_dotgraph as build_kin_dotgraph 

def updated_compound(c:Compound,**kwargs): 
    name,energy,idx,visible,fflags,conc,opts = c
    if kwargs.get('name',None) is not  None: 
        name = kwargs['name']
    if kwargs.get('energy',None) is not None: 
        energy = kwargs['energy']
    if kwargs.get('idx',None) is not None: 
        idx = kwargs['idx']
    if kwargs.get('visible',None) is not None: 
        visible = kwargs['visible']
    if kwargs.get('fflags',None) is not None: 
        fflags= kwargs['fflags']
    if kwargs.get('conc',None) is not None: 
        conc = kwargs['conc']
    if kwargs.get('opts',None) is not None: 
        opts = kwargs['opts']
    return Compound(name,energy,idx,visible,fflags,conc,opts)
def update_reaction(reaction:Reaction,idx2compound): 
    name,compounds,energy,idx,opts,visible = reaction
    reactants,products = compounds
    reactants = tuple(idx2compound[reactant.idx] for reactant in reactants)
    products = tuple(idx2compound[product.idx] for product in products)
    compounds = (reactants,products)
    return Reaction(name,compounds,energy,idx,opts,visible)

compounds_file = sys.argv[1]
reactions_file = sys.argv[2]
data_file = sys.argv[3]

nw_base = parser.parse_network_from_file(compounds_file, reactions_file)

data = np.loadtxt(data_file,dtype=float)
t = data[:,0] # time in s 
x = data[:,1:] # Concentrations in M

dot_dir = Path('gif_folder')
dot_dir.mkdir(exist_ok=True)
for i in range(len(t)): 
    if t[i]%50 == 0 and t[i] != 0: 
        new_compounds = []
        for compound in nw_base.compounds:
            conc = x[i,compound.idx]
            new_compounds.append(updated_compound(compound,conc=conc))
        idx2compound = {compound.idx:compound for compound in new_compounds}
        new_reactions = tuple(update_reaction(reaction,idx2compound) for reaction in nw_base.reactions)
        nw = Network(compounds=new_compounds,reactions=new_reactions)
        nw_snapshot = build_kin_dotgraph(nw)
        with open(dot_dir/f"snapshot_{t[i]:05.0f}.dot", 'w', encoding="utf8") as of:
            of.write(str(nw_snapshot))
