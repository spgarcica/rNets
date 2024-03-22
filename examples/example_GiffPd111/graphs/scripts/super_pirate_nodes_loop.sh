#!/bin/bash

base_graph="graph.dot"

# create images
dot -Tpng $base_graph -o "auto_layout_orig.png"
# retrieve properties in JSON format
dot -Tjson $base_graph -o props.json
# regex to fetch things from here
grep -n "^\s*\".*\"\s*\[" $base_graph > base_graph_info.temp
sed "/->/d" base_graph_info.temp > nodes_list.dat
sed -n "/->/p" base_graph_info.temp > edges_list.dat

### Now run the python script to get things
python process_pos.py


# And now adapt a list of graphs
readarray -t pos < positions_sel.dat
readarray -t pos2 < edge_positions_sel.dat
while read -r target ; do
	cp $target graph.temp
	echo $target
	i=0
	while read -r nd ; do
		ln=$(echo $nd | sed "s|:.*||g")
		sed -i "${ln}s/\[/\[ pos=\"${pos[$i]}\",/g" graph.temp
		i=$(($i+1))
	done < nodes_list.dat

	## add edges too!
	i=0
	while read -r ed ; do
		ln=$(echo $ed | sed "s|:.*||g")
		sed -i "${ln}s/\[/\[ pos=\"${pos2[$i]}\",/g" graph.temp
		i=$(($i+1))
	done < edges_list.dat

	nw_file=$(echo $target | sed "s|.dot|_nw.dot|g")
	nw_img=$(echo $target | sed "s|.dot|_nw.png|g")
	echo $nw_file
	mv graph.temp $nw_file

	# neato -n allows to read node positions and -n2, edge positions too
	neato -n2 -Tpng $nw_file -o $nw_img
done < graph_files.dat
