======================================
Regiospecific CO\ :sub:`2` \ fixation
======================================

In this example, we consider the reaction network for the regiospecific 
CO\ :sub:`2` \ fixation published in DOI: `10.1021/acs.organomet.9b00773 <https://www.dx.doi.org/10.1021/acs.organomet.9b00773>`__  
producing cyclic carbonates from a bicyclic epoxy alcohol and CO\ :sub:`2` \ , with bromide as a catalyst. 
More specifically, we showcase the integration of rNets with the knowledge graphs based on the OntoRXN ontology.
The files required for the generation of the reaction networks can be found in  
:code:`examples/example_KG` folder. This folder contains the following
files: 

.. code:: none

   example_KG
     -README
     -CycOct.owl
     -RNets_KG_Parser.py

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
`owlready2 <https://owlready2.readthedocs.io>`__. The following code will allow 
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

Here, we will generate the :code:`comps.csv` and :code:`reactions.csv` files. The :code:`--reference` option
allows to define a reference state to determine relative energies across the reaction network. In this case, 
there would be three reactants: EpOr+CO2+TMABr. Moreover, the :code:`--hidden-species` option allows to 
specify a comma-separated list of species that would have the :code:`visible` attribute set as False in the
compounds file.

Next we use rNets to generate the :code:`.dot` file containing the reaction 
network:

.. code:: shell-session
   
   $ python -m rNets comps.csv reactions.csv 

Finally we proceed to render the figure in our preferred graphical format using 
graphviz. In this case we will use :code:`png`

.. code:: shell-session

   $ dot -Tpng graph.dot -o graph.png 

