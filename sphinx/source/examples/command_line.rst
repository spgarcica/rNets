.. |example_01| graphviz:: ../resources/examples/example_01.dot

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

.. centered:: |example_01|

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

.. note::
   
   Currently under construction:
   Here we will cover the generation of a graph colored by thermodynamic data

Drawing a kinetic graph
-----------------------

.. note::
   
   Currently under construction:
   Here we will cover the generation of a graph colored by concentrations and 
   reaction rates. 

Using different energy units
----------------------------

.. note::
   
   Currently under construction:

   Here we will cover how to prepare a chemical configuration different from the 
   default one and how to use it.

Formatting our graph
--------------------

.. note::
   
   Currently under construction:
   Here we will cover how to prepare a graph configuration different from the 
   default one and how to use it.
