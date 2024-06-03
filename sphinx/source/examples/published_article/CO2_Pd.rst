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
Pd(111) colored by energies (figure 4 of the original rNets publication) whose 
files can be found in the :code:`examples/example_Pd111` folder. This folder 
contains the following files: 

.. code:: none

   example_Pd111
     -README
     assets
       -Pd_g.mkm
       -rm.mkm
       -theta.csv
     -parser_visual.py
     -run.py

Here the :code:`Pd_g.mkm` and :code:`rm.mkm` are files containing information 
similar to the Compounds and the Reactions files of rNets, but adjusted to the 
format used by `AMUSE <https://www.dx.doi.org/10.1039/D3DD00163F>`__ and the 
:code:`parser_visual.py` script is used to translate to the format of 
rNets' Compounds and Reactions files. 

Preliminary steps
.................

The first step is to translate to generate the rNet's Compounds and Reactions 
files. For this task we will use the :code:`parser_visual.py` which only requires 
to have installed the python libraries :code:`pandas` and :code:`numpy`. We can 
install them with: 

.. code:: python 

   python -m pip install numpy pandas

Quickstart
..........

For convenience we created the :code:`run.py` script which facilitates the 
generation of all the figures in one go (the present section and the following 
one). To execute the code the user will have to type in the following command: 

.. code:: shell-session

   python run.py

Upon execution two new folders will appear: :code:`temp` and :code:`res`. The 
:code:`temp` folder contains the .dot files, which serve as input to graphviz 
for the actual image generation. The :code:`res` folder will contain the 
automatically rendered .png files.

Generation of the network graphs
................................

Now, we proceed to carry out the translation using the :code:`parser_visual.py`
script. To use it we will execute the following command: 

.. code:: python
   
   python parser_visual.py -outfname_comp Pd_comp.csv -outfname_rx ./assets/Pd_reac.csv -in_comp ./assets/Pd_g.mkm -in_rx ./assets/rm.mkm -in_theta noc

With this the :code:`Pd_comp.csv` and :code:`Pd_reac.csv`  files will be 
generated, containing the reactions and the energetics of the reaction network 
in a suitable format for rNets.

.. note:: 

   Please note that the no file (:code:`noc`) has been passed to the :code:`-in_theta`

Next we use rNets to generate the :code:`.dot` file containing the reaction 
network:

.. code:: shell-session
   
   $ python -m rnets -cf Pd_comp.csv -rf Pd_reac.csv -o figure_4.dot

Finally we proceed to render the figure in our preferred graphical format using 
graphviz. In this case we will use :code:`png`

.. code:: shell-session

   $ dot -Tpng figure_4.dot -o figure_4.png


Kinetic representations
-----------------------

In this example the reaction network of the CO\ :sub:`2` \ hydrogenation on 
Pd(111) colored by concentration (figure 8 of the original rNets publication) whose 
files can be found in the :code:`examples/example_Pd111` folder. This folder 
contains the following files:

.. code:: none

   example_Pd111
     -README
     assets
       -Pd_g.mkm
       -rm.mkm
       -theta.csv
     -parser_visual.py
     -run.py

Here the :code:`Pd_g.mkm` and :code:`rm.mkm` are files containing information 
similar to the Compounds and the Reactions files of rNets, but adjusted to the 
format used by `AMUSE <https://www.dx.doi.org/10.1039/D3DD00163F>`__ and the 
:code:`parser_visual.py` script is used to translate to the format of 
rNets' Compounds and Reactions files. 

Preliminary steps
.................

The first step is to translate to generate the rNet's Compounds and Reactions 
files. For this task we will use the :code:`parser_visual.py` which only requires 
to have installed the python libraries :code:`pandas` and :code:`numpy`. We can 
install them with: 

.. code:: python 

   python -m pip install numpy pandas

Quickstart
..........

For convenience we created the :code:`run.py` script which facilitates the 
generation of all the figures in one go (the present section and the following 
one). To execute the code the user will have to type in the following command: 

.. code:: shell-session

   python run.py

Upon execution two new folders will appear: :code:`temp` and :code:`res`. The 
:code:`temp` folder contains the .dot files, which serve as input to graphviz 
for the actual image generation. The :code:`res` folder will contain the 
automatically rendered .png files.

Generation of the network graphs
................................

Now, we proceed to carry out the translation using the :code:`parser_visual.py`
script. To use it we will execute the following command: 

.. code:: python
   
   python parser_visual.py -outfname_comp Pd_comp.csv -outfname_rx ./assets/Pd_reac.csv -in_comp ./assets/Pd_g.mkm -in_rx ./assets/rm.mkm -in_theta noc

With this the :code:`Pd_comp.csv` and :code:`Pd_reac.csv`  files will be 
generated, containing the reactions and the energetics of the reaction network 
in a suitable format for rNets.

.. note:: 

   Please note that the file :code:`./assets/theta.csv` has been passed to the :code:`-in_theta`

Next we use rNets to generate the :code:`.dot` file containing the reaction 
network:

.. code:: shell-session
   
   $ python -m rnets -cf Pd_comp.csv -rf Pd_reac.csv -o figure_8.dot

Finally we proceed to render the figure in our preferred graphical format using 
graphviz. In this case we will use :code:`png`

.. code:: shell-session

   $ dot -Tpng figure_8.dot -o figure_8.png


An animation of the kinetic evolution
.....................................

Finally we need to convert all the :code:`.png` files into an animated gif. 
Specifically for the manuscript, imagemagick was used:  

.. code:: shell-session

   $ cd ..
   $ convert -delay 0 -loop 1 graph_{0..14}_nw.png Pd111_animation.gif
