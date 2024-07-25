import sys
from typing import Any
from collections.abc import Sequence
from pathlib import Path

import numpy as np

from rnets import parser
from rnets.struct import Network, Compound, Reaction
from rnets.plotter.kinetic import build_dotgraph as build_kin_dotgraph
from rnets.addons.colorbar import ColorbarCfg


type Model = np.ndarray[Any, np.dtype[np.float64]]


def updated_compound(c: Compound, **kwargs):
    name, energy, idx, visible, fflags, conc, opts = c
    if kwargs.get("name", None) is not None:
        name = kwargs["name"]
    if kwargs.get("energy", None) is not None:
        energy = kwargs["energy"]
    if kwargs.get("idx", None) is not None:
        idx = kwargs["idx"]
    if kwargs.get("visible", None) is not None:
        visible = kwargs["visible"]
    if kwargs.get("fflags", None) is not None:
        fflags = kwargs["fflags"]
    if kwargs.get("conc", None) is not None:
        conc = kwargs["conc"]
    if kwargs.get("opts", None) is not None:
        opts = kwargs["opts"]
    return Compound(name, energy, idx, visible, fflags, conc, opts)


def update_reaction(reaction: Reaction, idx2compound):
    name, compounds, energy, idx, opts, visible = reaction
    reactants, products = compounds
    reactants = tuple(idx2compound[reactant.idx] for reactant in reactants)
    products = tuple(idx2compound[product.idx] for product in products)
    compounds = (reactants, products)
    return Reaction(name, compounds, energy, idx, opts, visible)


def generate(
    cf: Path,
    rf: Path,
    model: np.ndarray[Any, np.dtype[np.float64]],
    op: Path,
) -> Sequence[Path]:
    nw_base = parser.parse_network_from_file(cf, rf)

    t = model[:, 0]  # time in s
    x = model[:, 1:]  # Concentrations in M

    snapshot_indices = [6000, 24000]

    def aux(i, ti):
        print(f"generating snapshot of t={ti}s")

        new_compounds = [
            updated_compound(compound, conc=x[i, compound.idx])
            for compound in nw_base.compounds
        ]

        idx2compound = {compound.idx: compound for compound in new_compounds}
        new_reactions = tuple(
            update_reaction(reaction, idx2compound) for reaction in nw_base.reactions
        )

        nw = Network(compounds=new_compounds, reactions=new_reactions)
        nw_snapshot = build_kin_dotgraph(nw,colorbar_cfg=ColorbarCfg(anchor="[I+N+W+W]"))
        f = Path(op / f"snapshot_{ti:05.0f}.dot")
        f.write_text(str(nw_snapshot), encoding="utf8")
        return f

    return [aux(i, ti) for i, ti in enumerate(t) if i in snapshot_indices]


if __name__ == "__main__":
    import kinetic_model

    cf, rf, m = map(Path, sys.argv[1:])
    model = kinetic_model.generate(m)
    if model is None:
        exit(1)

    generate(cf, rf, model, Path("."))
