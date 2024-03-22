import json
import re

with open("props.json","r") as finp:
    data = json.load(finp)

# Info from nodes
nodes = data["objects"]
pos_info = {item["name"]:item["pos"] for item in nodes}

with open("nodes_list.dat","r") as fnd:
    raw_dump = [line.strip().split(":")[1] for line in fnd.readlines()]
    node_list = [item.strip().replace("\"","").replace("[","").replace(" ","") for item in raw_dump]
print(node_list)
block = ""
for nd in node_list:
    print(nd,pos_info[nd])
    block += pos_info[nd] + "!\n"
with open("positions_sel.dat","w") as fout:
    fout.write(block)

# Processing edges: map with tail and head and locate pos to get the curves
edges = data["edges"]

with open("edges_list.dat","r") as fed:
    raw_dump = [line.strip().split(":")[1] for line in fed.readlines()]
    edge_list = [item.strip().replace("\"","").replace("[","") for item in raw_dump]
    

edge_mapping = {}
for ed in edges:
    start = nodes[int(ed["head"])]["name"]
    end = nodes[int(ed["tail"])]["name"]
    edgestr = "%s -> %s" % (start,end)
    edgestr2 = "%s -> %s" % (end,start)
    edge_mapping[edgestr] = ed["pos"]
    edge_mapping[edgestr2] = ed["pos"]

# now dump this in the correct order
block2 = ""
for edstr in edge_list:
    block2 += edge_mapping[edstr] + "\n"


with open("edge_positions_sel.dat","w") as fout:
    fout.write(block2)
