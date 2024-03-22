#!/bin/bash

arr=(0 1000 2500 5000 8000 8500 9250 9350 9450 9500 9650 9750 10000 10250 11914)

for i in ${!arr[@]}
do 
	python tests.py Pd_comp_${arr[$i]}.csv Pd_reac_${arr[$i]}.csv "kin" 
	cp graph.dot ./graphs/graph_$i.dot
done
