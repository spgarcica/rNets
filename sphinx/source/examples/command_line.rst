.. |example_00| graphviz:: ../resources/examples/example_00.dot
.. |example_01| graphviz:: ../resources/examples/example_01.dot
.. |example_02| graphviz:: ../resources/examples/example_02.dot
.. |example_03| graphviz:: ../resources/examples/example_03.dot

=======================
Command-line Examples
=======================

For the most basic usage of rNets through its command-line interface we recommend 
checking first the :doc:`../quick_start/basic_usage`. In this section, more 
more comprehensive examples covering more detailed graph customization will be 
included. 

My first reaction graph
-----------------------

To introduce the minimal components of rNets we will create 
a very simple reaction network, which is shown below: 

.. centered:: |example_00|

First we will start writing the :code:`Reactions` file and then we will 
write the :code:`Compounds` file. In this case we have 2 reactions, 
:code:`A -> B` and :code:`B + C -> D`. To create our csv we will start with the 
following table, which we can create in your preferred spreadsheet editor: 

+---------+---------+-------------+----------+----------+--------+
|  cleft  |  cleft  |  direction  |  cright  |  energy  |  name  |
+---------+---------+-------------+----------+----------+--------+
|         |         |             |          |          |        |
+---------+---------+-------------+----------+----------+--------+

The details of each column are explained in the 
:doc:`../quick_start/file_formats` but the key thing here is that we have one 
reaction that has 2 reactants but no reaction leading to the formation of 2 
products we will only need one :code:`cright` (Compound at the RIGHT side of the
reaction) column.

Now we can proceed to add the first reaction: 

+---------+---------+-------------+----------+----------+--------+
|  cleft  |  cleft  |  direction  |  cright  |  energy  |  name  |  
+---------+---------+-------------+----------+----------+--------+
|    A    |         |      ->     |    B     |    1.0   |   R1   |
+---------+---------+-------------+----------+----------+--------+ 

If we were to save the file with our editor as a csv it would look like: 

.. code:: none 
   
   cleft,cleft,direction,cright,energy,name
   A,,->,B,1.0,R1

.. note::

   We are currently adding an :code:`energy` of :code:`1.0eV`. This value is not
   important for getting the reaction network right, but will impact the coloring
   and thickness of the arrows in the next examples. 

Now we add the second reaction: 

+---------+---------+-------------+----------+----------+--------+
|  cleft  |  cleft  |  direction  |  cright  |  energy  |  name  |  
+---------+---------+-------------+----------+----------+--------+
|    A    |         |      ->     |    B     |    1.0   |   R1   |
+---------+---------+-------------+----------+----------+--------+ 
|    B    |    C    |      ->     |    D     |    1.0   |   R2   |
+---------+---------+-------------+----------+----------+--------+ 

which we will save as the file :code:`reactions.csv`. 

.. code:: none 

   cleft,cleft,direction,cright,energy,name
   A,,->,B,1.0,R1
   B,C,->,D,1.0,R2

.. note:: 

   Please notice how the second cleft column has been left empty for the first 
   reaction. If the second reaction did not involve a second reactant we could 
   have completely removed the column, or left it with empty spaces and in both 
   cases rNets will properly treat the reactions as unimolecular reactions. 

Now that we know all species involved in the reactions we can write the 
:code:`Compounds` file which. As it is also a csv file we will again use our 
spreadsheet editor for generating the table: 

+---------+---------+
|   name  |  energy |
+---------+---------+
|    A    |   0.0   |
+---------+---------+
|    B    |   0.0   |
+---------+---------+
|    C    |   0.0   |
+---------+---------+
|    D    |   0.0   |
+---------+---------+

When we save the table as the csv file :code:`compounds.csv` it will look like: 

.. code:: none

   name,energy
   A,0.0
   B,0.0
   C,0.0
   D,0.0

.. note::

   Again, for this example we will use the value of :code:`0.0eV` for the energies
   :code:`energy` without paying much attention to it, as we are only interested 
   in generating an initial graph.  

Now that we have created both of our input files, the last two steps are to 
generate the dot file and the image file, these steps are exactly as it is shown
in the :doc:`../quick_start/basic_usage`.

.. code::

   $ python -m rnets -cf compounds.csv -rf reactions.csv -o reaction_network.dot
   $ dot -Tpng reaction_network.dot -o reaction_network.png 

If we want an editable image we recommend doing the final conversion to an svg 
instead of a png: 

.. code:: shell-session

   $ dot -Tsvg reaction_network.dot -o reaction_network.svg



Drawing a thermodynamic graph
-----------------------------

For rNets, the absence of information about concentrations in the 
:code:`compounds.csv` will always lead to an energy-based representation. So 
the only difference with `My first reaction graph`_ example is that this time we will 
be providing different energy values. Let's assume that we updated the energies 
of the previous tables to generate the :code:`reactions.csv` and
:code:`compounds.csv` files respectively

.. code:: none 

   cleft,cleft,direction,cright,energy,name
   A,,->,B,4.0,R1
   B,C,->,D,7.0,R2

.. code:: none

   name,energy
   A,0.0
   B,1.0
   C,0.0
   D,-2.0

After updating the energy values of :code:`reactions.csv` and 
:code:`compounds.csv` we can proceed with the generation of the graph. 

.. code::

   $ python -m rnets -cf compounds.csv -rf reactions.csv -o reaction_network.dot
   $ dot -Tpng reaction_network.dot -o reaction_network.png 

The resulting graph will look like: 

.. centered:: |example_01|

If we compare it with the graph generated in `My first reaction graph`_ example 
we can now observe how, with the default color scheme, the most stable compounds
are colored in a darker color ( :code:`D` ) while the least stable compounds 
( :code:`B` ) are in a lighter color. Also we can observe how the reaction with 
the lowest barrier has a thicker and darker color than the other reaction.  


Drawing a kinetic graph
-----------------------

As indicated in the previous section, the absence of information about 
concentrations in the :code:`compounds.csv` will lead to an energy-based 
representation. So, in order to change to a concentration-based representation 
we need to first update our :code:`compounds.csv` which we can do directly on 
the file or using a spreadsheet editor.

+---------+---------+---------+
|   name  |  energy |   conc  |
+---------+---------+---------+
|    A    |   0.0   |   0.75  |
+---------+---------+---------+
|    B    |   1.0   |   0.1   |
+---------+---------+---------+
|    C    |   0.0   |   1.0   |
+---------+---------+---------+
|    D    |  -2.0   |   0.25  |
+---------+---------+---------+

After adding the concentration column and saving our file as a .csv it will look
like this: 

.. code:: none

   name,energy,conc
   A,0.0,0.75
   B,1.0,0.1
   C,0.0,1.0
   D,-2.0,0.25

The :code:`reactions.csv` file instead, requires no further change, so we will 
borrow it from the `Drawing a thermodynamic graph`_ example: 

.. code:: none 

   cleft,cleft,direction,cright,energy,name
   A,,->,B,4.0,R1
   B,C,->,D,7.0,R2

After updating our :code:`compounds.csv` and with the already prepared 
:code:`reactions.csv` we can proceed with the generation of the graph. 

.. code::

   $ python -m rnets -cf compounds.csv -rf reactions.csv -o reaction_network.dot
   $ dot -Tpng reaction_network.dot -o reaction_network.png 

The resulting graph will look like: 

.. centered:: |example_02|
   
Compared with the previous two examples we can observe clear differences. Same 
as the `Drawing a thermodynamic graph`_ example, the colors of the different 
in this case are light for compounds in high concentration, while dark colors 
corresponds to low concentration species. The major difference with the previous
two examples is in the arrows. The arrows here represent the net reaction rate, 
a thicker arrow means a larger net rate and a thinner one a lower net rate. The 
direction of the arrow shows which species are being mainly generated and which 
ones are being mainly consumed. This feature is specially interesting when 
dealing with complex reaction networks where the concentration effects are 
difficult to predict, as it provides a visual cue.

Using different energy units
----------------------------

In this example we will get introduced to the chemical configuration class
( :code:`rnets.chemistry.ChemCfg` ). to illustrate its usage we will borrow the 
`Drawing a kinetic graph`_ example. 

First, we are going to rewrite our :code:`compounds.csv` and 
:code:`reactions.csv` in :code:`kcal/mol` which we can easily do in our 
preferred spreadsheet editor. 

+---------+---------+---------+-------------+
|   name  |  energy |   conc  |  energy(eV) |
+---------+---------+---------+-------------+
|    A    |   0.0   |   0.75  |     0.0     |
+---------+---------+---------+-------------+
|    B    |  23.1   |   0.1   |     1.0     |
+---------+---------+---------+-------------+
|    C    |   0.0   |   1.0   |     0.0     |
+---------+---------+---------+-------------+
|    D    | -46.1   |   0.25  |    -2.0     |
+---------+---------+---------+-------------+

We remove the :code:`energy(eV)` column and save the file as a csv

.. code:: none

   name,energy,conc
   A,0.0,0.75
   B,23.1,0.1
   C,0.0,1.0
   D,-46.1,0.25

We proceed similarly with the :code:`reactions.csv` obtaining the file: 

.. code:: none 

   cleft,cleft,direction,cright,energy,name
   A,,->,B,92.2,R1
   B,C,->,D,161.4,R2

The next, we proceed to generate the :code:`.dot` file as we did in the previous 
examples. However, this time we need to specify the energy units within the 
command: 

.. code::

   $ python -m rnets -cf compounds.csv -rf reactions.csv -o reaction_network.dot --units kcal/mol
   $ dot -Tpng reaction_network.dot -o reaction_network.png 

.. centered:: |example_03|

If the energies provided were at a reference state of 500K we would need to 
specify also the temperature in the command line: 

.. code::

   $ python -m rnets -cf compounds.csv -rf reactions.csv -o reaction_network.dot --units kcal/mol --temperature 500


Formatting our graph
--------------------

.. note::
   
   Currently under construction:
   Here we will cover how to prepare a graph configuration different from the 
   default one and how to use it.
