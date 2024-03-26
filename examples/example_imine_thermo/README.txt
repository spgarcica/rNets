In this folder there are 4 different reaction networks. 

a) 'comps_paper_simple.csv' and 'reactions_paper_simple.csv'
b) 'comps_32_simple.csv' and 'reactions_32_simple.csv' 
c) 'comps_paper.csv' and 'reactions_paper.csv' 
d) 'comps_32.csv' and 'reactions_32.csv' 

The files with the termination "simple.csv" include the ones required to 
generate the figures as presented in the manuscript. The files without the 
termination "simple.csv" correspond to the full reaction network. All the 
numerical values included in these files come from the original publication
(DOI: 10.1021/acs.orglett.0c00367). Specifically, the files in a) are used 
to generate Figure 3a in the main text of the rnets publication. The files in
b) correspond to the files required to generate Figure 3b. Inkscape was used 
to compose both figures into a single figure. 

The files in c) are the non-simplified reaction network of Figure 3a, included
in the SI as Figure SX. The files in d) are the non-simplified reaction network
of Figure 3b, included in the SI as Figure SY.  

To illustrate the generation of any of these figures I will use as example
the generation of Figure 3a. 

First we will generate the .dot file containing the reaction network from 
the compounds and reactions files. To do so we execute the following line: 

python generate_dotfile.py comps_paper_simple.csv reactions_paper_simple.csv figure_3a.dot

This will generate a file named figure_3a.dot in the current directory. Next we 
will render the figure with graphviz. We will generate a .png file, but other 
formats such as svg are also possible. To do so, we will execute the following
command: 

dot -Tpng figure_3a.dot -o figure_3a.png

With this we have generated the image of the reaction network. 

Note: 

Please note that within generate_dotfile.py, a custom treatment for the "simple"
files is included. This is not necessary to generate a reaction network graph, 
but it was used to add some control over the final layout to guarantee that
the resulting figure would fit in the manuscript. It has also been added 
to the examples to ensure the reproducibility of the figures in the article. 


