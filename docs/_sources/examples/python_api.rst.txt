.. |example_01| graphviz:: ../resources/examples/example_01.dot

=======================
Python API Examples
=======================

In this section we will cover examples using directly the python API interface
instead of the command line. The usage of the python API facilitates the 
integration of python libraries such as pykinetic, which will also be covered
in the examples. 


My first reaction Graph
-----------------------

To introduce the basic components of the python API of rNets we will create 
a very simple reaction network, which is shown below: 

.. centered:: |example_01|

.. code:: python
   
   from rnets.chemistry import Compound,Reaction
   from rnets.struct import Network
   from rnets.plotter.thermo import build_dotgraph
   from collections import Counter
   
   A = Compound('A',0.0,0) 
   B = Compound('B',1.0,1) 
   C = Compound('C',0.0,2) 
   D = Compound('D',-2.0,3)
   
   r1 = Reaction('r1',((A,),(B,)),20.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),20.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))
   
   nw_test = build_dotgraph(nw)
   with open("example1.dot", 'w', encoding="utf8") as of:
       of.write(str(nw_test))

A thermodynamic Graph
---------------------

Here we will cover the generation of a graph colored by thermodynamic data

A kinetic Graph
---------------

Here we will cover the generation of a graph colored by concentrations and 
reaction rates. 

Using different energy units
----------------------------

Here we will cover how to prepare a chemical configuration different from the 
default one and how to use it.

Formatting our graph
--------------------

Here we will cover how to prepare a graph configuration different from the 
default one and how to use it.

Integration with other software: Pykinetic (thermo)
---------------------------------------------------

An example of how to adapt pykinetics classes to generate a thermodynamic graph

Integration with other software: Pykinetic (kinetic)
----------------------------------------------------

An example of how to adapt pykinetics classes to generate a kinetic graph
