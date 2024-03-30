======================================
Regiospecific CO\ :sub:`2` \ fixation
======================================

In this example the reaction network of the regiospecific CO\ :sub:`2` \ fixation
is shown. This example shows the integration of knowledge graphs and rNets. The files 
required for the generation of the reaction networks can be found in  
:code:`examples/example_KG` folder. This folder contains the following
files: 

.. code:: none

   example_KG
     -README
     -CycOct.owl
     -RNets_KG_Parser.py

Here the :code:`owl` file is a file containing the information of the knowledge
graph, typically used in non-relational databases for knowledge graphs. 
Specifically, it was generated using
`ontorxn_tools <https://gitlab.com/dgarayr/ontorxn_tools>`__ . The file 
:code:`RNets_KG_Parser.py` allows the translation of the :code:`owl` file to 
the input files of :code:`rNets`. 

Preliminary steps
.................

The file :code:`RNets_KG_Parser.py` has dependencies to two python libraries: 
`rdflib <https://github.com/RDFLib/rdflib>` and 
`owlready2 <https://owlready2.readthedocs.io>`. The following code will allow 
you to install both of these libraries, but in case of doubt we recommend to 
follow their official documentation to install them. 

.. code:: shell-session
   
   $ python -m pip install rdflib owlready2

Generation of the network graph
...............................

In order to generate the graph from the :code:`owl` file we will first use the 
:code:`RNets_KG_Parser.py` whose contents are shown below: 

.. highlight:: python 

.. literalinclude:: ../../../../examples/example_KG/RNets_KG_Parser.py

.. highlight:: default

To use the script to generate the Compounds and Reactions files needed for rNets
we will execute the following command: 

.. code:: shell-session

   $ python RNets_KG_Parser.py comps.csv reactions.csv CycOct.owl --reference EpOr+CO2+TMABr --hidden-species CO2,TMA,TMABr

Here, we will generate the :code:`comps.csv` and :code:`reactions.csv` files 
that will have as reference state in energy the :code:`EpOr+CO2+TMABr` of the 
knowledge graph and will set the species :code:`CO2`, :code:`TMA` and 
:code:`TMABr` as not visible. 

Next we use rNets to generate the :code:`.dot` file containing the reaction 
network:

.. code:: shell-session
   
   $ python -m rNets comps.csv reactions.csv 

Finally we proceed to render the figure in our preferred graphical format using 
graphviz. In this case we will use :code:`png`

.. code:: shell-session

   $ dot -Tpng graph.dot -o graph.png 

