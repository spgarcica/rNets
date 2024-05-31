import argparse

import pandas as pd
import numpy as np


COLUMNS_REACT = ["name", "energy", "fflags", "visible", "opts", "conc"]

COLUMNS_RXS = [
    "cleft",
    "cleft",
    "cright",
    "cright",
    "energy",
    "direction",
    "name",
    "visible",
]


def reader(path: str) -> list:
    with open(path, "r") as inf:
        data = [line.strip().split() for line in inf]
    return data


def generate_intermediate(intermediates, in_theta, outfname_comp):
    names_intermediates = [
        line[0][:-1]
        for line in intermediates
        if not not line and ("i" in line[0] or "g" in line[0])
    ]

    energy_intermediates = [
        float(line[1])
        for line in intermediates
        if not not line and ("i" in line[0] or "g" in line[0])
    ]

    fflags = ["i" if "g" in name else "" for name in names_intermediates]

    visibles = ["" for _ in names_intermediates]

    opts = visibles

    if in_theta == "noc":
        conc = ["" for _ in names_intermediates]
    else:
        conc = list(pd.read_csv(in_theta)["theta"])

    intermediates_dict = dict(
        zip(
            COLUMNS_REACT,
            [names_intermediates, energy_intermediates, fflags, visibles, opts, conc],
        )
    )
    intermediates_df = pd.DataFrame(intermediates_dict)

    intermediates_df.to_csv(outfname_comp, index=False)

    return names_intermediates


def generate_reactions(rxs, names_intermediates, intermediates, outfname_rx):
    clefts = []
    crights = []

    for item in rxs:
        cleft = []
        cright = []
        if not item or ":" in item[1]:
            continue
        else:
            row_index = item.index("->")

            for index, subitem in enumerate(item):
                if subitem in names_intermediates and index < row_index:
                    cleft.append(subitem)
                elif subitem in names_intermediates and index > row_index:
                    cright.append(subitem)
                else:
                    continue
            if len(cleft) == 1:
                cleft.append("")
            else:
                cleft = cleft
            if len(cright) == 1:
                cright.append("")
            else:
                cright = cright
            clefts.append(cleft)
            crights.append(cright)

    names_rxs = [
        line[0][:-1] for line in intermediates if not not line and "R" in line[0]
    ]

    energies_rxs = [
        float(line[1]) for line in intermediates if not not line and "R" in line[0]
    ]

    directions = ["<->" for _ in names_rxs]

    clefts1, clefts2 = np.asarray(clefts)[:, 0], np.asarray(clefts)[:, 1]

    crights1, crights2 = np.asarray(crights)[:, 0], np.asarray(crights)[:, 1]

    visibles_rx = ["" for _ in names_rxs]

    reactions_df = pd.DataFrame(
        np.asarray(
            [
                list(clefts1),
                list(clefts2),
                list(crights1),
                list(crights2),
                energies_rxs,
                directions,
                names_rxs,
                visibles_rx,
            ]
        ).T,
        columns=COLUMNS_RXS,
    )

    reactions_df.to_csv(outfname_rx, index=False)


def parser():
    p = argparse.ArgumentParser(description="Parse AMUSE outputs for visualization")
    p.add_argument(
        "-outfname_comp",
        metavar="outfname_comp",
        type=str,
        help="Provide the name for the compounds output.",
    )
    p.add_argument(
        "-outfname_rx",
        metavar="outfname_rx",
        type=str,
        help="Provide the name for the reactions output.",
    )
    p.add_argument(
        "-in_comp",
        metavar="in_comp",
        type=str,
        help="Provide the path to the g.mkm file.",
    )
    p.add_argument(
        "-in_rx", metavar="in_rx", type=str, help="Provide the path to the rm.mkm file."
    )
    p.add_argument(
        "-in_theta",
        metavar="in_theta",
        type=str,
        help="Provide the path to the file containing the composition. If no concentration is provided, type noc.",
    )

    return p


def main():
    args = parser().parse_args()

    outfname_comp = str(args.outfname_comp)
    outfname_rx = str(args.outfname_rx)
    in_comp = str(args.in_comp)
    in_rx = str(args.in_rx)
    in_theta = str(args.in_theta)

    intermediates = reader(in_comp)
    rxs = reader(in_rx)

    names = generate_intermediate(intermediates, in_theta, outfname_comp)
    generate_reactions(rxs, names, intermediates, outfname_rx)


if __name__ == "__main__":
    main()
