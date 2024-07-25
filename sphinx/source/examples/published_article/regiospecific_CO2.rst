======================================
Regiospecific CO\ :sub:`2` \ fixation
======================================

In this example, we consider the reaction network for the regiospecific 
CO\ :sub:`2` \ fixation published in DOI: 
`10.1021/acs.organomet.9b00773 <https://www.dx.doi.org/10.1021/acs.organomet.9b00773>`__  
producing cyclic carbonates from a bicyclic epoxy alcohol and CO\ :sub:`2` \ , 
with bromide as a catalyst. More specifically, we showcase the integration of 
rNets with the knowledge graphs based on the OntoRXN ontology.
The files required for the generation of the reaction networks can be found in  
:code:`examples/example_KG` folder. This folder contains the following
files: 

.. code:: none

   example_KG
     -README
     -CycOct.owl
     -RNets_KG_Parser.py
     -run.py

Here the :code:`owl` file contains a knowledge graph (non-relational database) craterd
through the Python library `ontorxn_tools <https://gitlab.com/dgarayr/ontorxn_tools>`__, 
employing the `OntoRXN <https://gitlab.com/dgarayr/ontorxn>`__ ontology as the data 
organization scheme. From there, the file 
:code:`RNets_KG_Parser.py` allows the translation of the :code:`owl` file to 
the input files of :code:`rNets`. 

Preliminary steps
.................

The file :code:`RNets_KG_Parser.py` has dependencies to two python libraries: 
`rdflib <https://github.com/RDFLib/rdflib>`__ and 
`owlready2 <https://owlready2.readthedocs.io>`__ as well as numpy. The following 
code will allow you to install both of these libraries, but in case of doubt we 
recommend to follow their official documentation to install them. 

.. code:: shell-session
   
   $ python -m pip install rdflib owlready2 numpy

.. note::
  
   The specific versions used were: 
   *  numpy 1.26.4
   *  owlready2 0.46 
   *  rdflib 7.0.0

Quickstart
..........

For convenience we created the :code:`run.py` script which facilitates the 
generation of all the figures in one go. To execute the code the user 
will have to type in the following command: 

.. code:: shell-session

   python run.py

Upon execution two new folders will appear: :code:`temp` and :code:`res`. The 
:code:`temp` folder contains the .dot files, which serve as input to graphviz 
for the actual image generation. The :code:`res` folder will contain the 
automatically rendered .png files.

Generation of the network graph
...............................

In order to generate the graph from the :code:`owl` file we will first use the 
:code:`RNets_KG_Parser.py`.

To use the script to generate the Compounds and Reactions files needed for rNets
we will execute the following command: 

.. code:: shell-session

   $ python RNets_KG_Parser.py CycOct_comps.csv CycOct_reactions.csv CycOct.owl --reference EpOr+CO2+TMABr --hidden-species CO2,TMA,TMABr

The two first arguments are the **compounds** (`CycOct_comps.csv`) and **reactions**
(`CycOct_reactions.csv`) that will be read by rNets, followed by the name of the
target `.owl` file (`CycOct.owl`). The optional arguments control:

*  :code:`--reference`: Species used to determine the energy reference, separated by 
   "+" symbol. In this case, we select the initial reactants and catalyst for the 
   proposed process: :code:`EpOr+CO2+TMABr`.
*  :code:`--hidden-species`: Comma-separated list of species which will not be assigned
   a node in the produced DOT file, but will be considered to balance energies. 

In absence of these arguments, the graph will still be generated, but with a 
more complex layout (as in Figure S2 in the SI), and the energies in the 
compounds and reaction files will be absolute. 

Next we use rNets to generate the :code:`.dot` file containing the reaction 
network:

.. code:: shell-session
   
   $ python -m rnets -cf CycOct_comps.csv -rf CycOct_reactions.csv -o CycOct_network.dot 

Finally we proceed to render the figure in our preferred graphical format using 
graphviz. In this case we will use :code:`png`

.. code:: shell-session

   $ dot -Tpng CycOct_network.dot -o CycOct_network.png

To get the horizontal layout in shown in the manuscript, the corresponding graph
argument should be passed to :code:`dot`, setting :code:`rankdir` to :code:`LR` 
(left-right) instead of the default :code:`TB` (top-bottom):

.. code:: shell-session

   $ dot -Grankdir=LR -Nfontsize=16 -Granksep=0.1 Gnodesep=0.5 -Tpng CycOct_network.dot -o CycOct_network_horizontal.png

For details on CRN-KG generation, check the corresponding article
`Garay-Ruiz and Bo, J. Cheminf. 2022, 14, 29 <(doi.org/10.1186/s13321-022-00610-x)>`__

