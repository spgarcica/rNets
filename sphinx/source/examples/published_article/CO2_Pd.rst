=======================================
CO\ :sub:`2` \ hydrogenation on Pd(111)
=======================================

.. contents::
   :backlinks: none
   :depth: 2
   :local:


Thermodynamic representations
-----------------------------

In this example the reaction network of the CO\ :sub:`2` \ hydrogenation on 
Pd(111) whose files can be found in the :code:`examples/example_Pd111` folder. 
This folder contains the following files: 

.. code:: none

   example_Pd111
     -README
     -Pd_g.mkm
     -rm.mkm
     -theta.csv
     -parser_visual.py

Here the :code:`Pd_g.mkm` and :code:`rm.mkm` are files containing information 
similar to the Compounds and the Reactions files of rNets, but adjusted to the 
format used by `AMUSE <https://www.dx.doi.org/10.1039/D3DD00163F>`__ and the 
:code:`parser_visual.py` script is used to translate to the format of 
rNets' Compounds and Reactions files. 

Preliminary steps
.................

The first step is to translate to generate the rNet's Compounds and Reactions 
files. For this task we will use the :code:`parser_visual.py` which only requires 
to have installed the python libraries :code:`pandas` and :code:`numpy`.

Generation of the network graphs
................................

Now, we proceed to carry out the translation using :code:`parser_visual.py` whose  
contents are shown below: 

.. highlight:: python 

.. literalinclude:: ../../../../examples/example_Pd111/parser_visual.py

.. highlight:: default

To use it we will execute the following command: 

.. code:: shell-session

   $ python parser_visual.py -outfname_comp Pd_comp.csv -outfname_rx Pd_reac.csv -in_comp Pd_g.mkm -in_rx rm.mkm -in_theta theta.csv

This command will generate the files :code:`Pd_comp.csv` and :code:`Pd_reac.csv` 
which are the rNets' Compounds and Reactions files. To do so it will use the 
:code:`Pd_g.mkm` and :code:`rm.mkm` and :code:`theta.csv`

Next we use rNets to generate the :code:`.dot` file containing the reaction 
network:

.. code:: shell-session
   
   $ python -m rNets Pd_comp.csv Pd_reac.csv

Finally we proceed to render the figure in our preferred graphical format using 
graphviz. In this case we will use :code:`png`

.. code:: shell-session

   $ dot -Tpng graph.dot -o graph.png 


Kinetic representations
-----------------------

In this example the reaction network of the CO\ :sub:`2` \ hydrogenation on 
Pd(111) as it evolves during a kinetic simulation. The files can be found in 
the :code:`examples/example_GiffPd111` folder which contains the following files:

   a)  :code:`Pd_comp_*.csv` 
   b)  :code:`Pd_reac_*.csv` 
   c)  :code:`theta_*.csv` 
   d)  :code:`tests.py`
   e)  :code:`do_graph.sh`
   f)  :code:`graph.dot`
   g)  :code:`graphs/scripts` folders

The files in :code:`a` , :code:`b` and :code:`c` correspond to the files at 
different times during the simulation. The scripts :code:`tests.py` , 
:code:`do_graph.sh` and the files contained in :code:`graphs/scripts` are used 
for the generation of the :code:`dot` files using rNets as well as to ensure
a consistent graph layout for the generation of an animated GIF. 

First we will execute the :code:`do_graphs.sh` script which uses the 
:code:`tests.py` : 

.. code:: shell-session

   $ bash do_graphs.sh 

This will generate all the required dotfiles, but to ensure a persistent layout 
we need to use the contents of the :code:`graphs/scripts` so we need to move 
into the folder: 

.. code:: shell-session

   $ cd graphs/scripts

Now we execute the :code:`generate_kinetic_graphs.sh` script which will take 
care of having a consistent layout as well as the generation of the :code:`png`
files.

.. code:: shell-session

   $ bash generate_kinetic_graphs.sh

This will generate snapshots of the network in :code:`code`

An animation of the kinetic evolution
.....................................

Finally we need to convert all the :code:`.png` files into an animated gif. 
Specifically for the manuscript, imagemagick was used:  

.. code:: shell-session

   $ convert -delay 0 -loop 1 *.png Pd111_animation.gif

