==================
Imine condensation
==================

.. contents::
   :backlinks: none
   :depth: 2
   :local:

Thermodynamic representations
-----------------------------

The files required for the generation of the reaction networks of the imine 
condensation example of the rNets' article can be found in the 
:code:`examples/example_imine_thermo` folder. This folder contains the following
files: 

.. code:: none

   example_imine_thermo
     -README.txt
     -comps_paper.csv
     -reactions_paper.csv
     -comps_paper_simple.csv
     -reactions_paper_simple.csv
     -comps_32.csv
     -reactions_32.csv
     -comps_32_simple.csv
     -reactions_32_simple.csv
     -generate_dotfile.py
     -figure_3b.dot
     -figure_3a.dot
     -figure_S3.dot
     -figure_S4.dot

Here we have 4 different compound-reaction file pairs: 

   a) :code:`comps_paper_simple.csv` and :code:`reactions_paper_simple.csv`
   b) :code:`comps_32_simple.csv` and :code:`reactions_32_simple.csv` 
   c) :code:`comps_paper.csv` and :code:`reactions_paper.csv` 
   d) :code:`comps_32.csv` and :code:`reactions_32.csv` 

The files with the termination :code:`simple.csv` include the ones required to 
generate the figures as presented in the manuscript. The files without the 
termination :code:`simple.csv` correspond to the full reaction network. All the 
numerical values included in these files come from the original publication
(DOI: `10.1021/acs.orglett.0c00367 <https://www.dx.doi.org/10.1021/acs.orglett.0c00367>`__).
Specifically, the files in :code:`a` are used to generate a simplified reaction 
network with the uncorrected DFT energies, hiding some compounds and species. 
The files in :code:`b` are used to generate the same representation of the network 
but with a corrected set of energies. The files in :code:`c` are the uncorrected 
full reaction network and the files in :code:`d` are used for the corrected full 
reaction network.

The procedure for the generation of all images is the same one, only needing to 
change the compounds and reactions files. We will use the files in :code:`a` (
uncorrected and simplified reaction network ) to illustrate the procedure. 

Preliminary steps
.................

For the present example the only required software is rNets and graphviz. Please
follow the installation instructions of rNets.

Generation of the network graphs
................................

First we will generate the .dot file containing the reaction network from 
the compounds and reactions files. To do so we execute the following line:

.. code:: shell-session

   $ python generate_dotfile.py comps_paper_simple.csv reactions_paper_simple.csv figure_3a.dot

his will generate a file named figure_3a.dot in the current directory. Next we 
will render the figure with graphviz. We will generate a .png file, but other 
formats such as svg are also possible. To do so, we will execute the following
command: 

.. code:: shell-session

   $ dot -Tpng figure_3a.dot -o figure_3a.png

With this we have generated the image of the reaction network. 

.. note::

   Please note that within generate_dotfile.py, a custom treatment for the 
   :code:`simple.csv` files is included. This is not necessary to generate a 
   reaction network graph, but it was used to add some control over the final 
   layout to guarantee that the resulting figure would fit in the manuscript. It 
   has also been added to the examples to ensure the reproducibility of the figures
   in the article. 


Kinetic representations
-----------------------

The files required for the generation of the reaction networks of the imine 
condensation example of the rNets' article can be found in the 
:code:`examples/example_imine_kinetic` folder. This folder contains the following
files: 

.. code:: none

   example_imine_kinetic
    -README.txt
    -comps_draco_42.csv
    -reactions_draco_42.csv
    -comps_draco_42_simple.csv
    -reactions_draco_42_simple.csv
    -kinetic_model.py
    -kinetic_model.index
    -generate_kinetic_snapshots.py
    -generate_kinetic_gif.py

Here we have 4 different types of files: 

   a) :code:`comps_draco_42_simple.csv` , :code:`reactions_draco_42_simple.csv`,
      :code:`comps_draco_42.csv`, :code:`reactions_draco_42.csv`
   b) :code:`kinetic_model.py` , :code:`kinetic_model.index`
   c) :code:`generate_kinetic_snapshots.py`  
   d) :code:`generate_kinetic_gif.py`  

Files in :code:`a` are used to create the reaction network and provide the energetics
needed to compute the kinetic constants and thus the net rates of the 
reactions. Files in :code:`b` are files generated using the **pykinetic** 
software, the :code:`.index` file contains similar information to the rNets 
compounds and reaction files, to simplify re-creating the input needed for **pykinetic**. 
The :code:`kinetic_model.py` contains how to carry out the actual microkinetic 
simulation, and will generate a :code:`.data` file containing the concentrations 
at each time of all species. The file in :code:`c` is a script to generate the 
:code:`.dot` files at different times, which are used in the generation the 
static graph figures which are the focus of the present section. The file in 
:code:`d` is a script to generate all the :code:`.dot` files required to 
generate the :code:`.gif` file which is the focus of the following section.

The files with the termination :code:`simple.csv` are used to draw a simplified
version of the reaction network. The files without the termination 
:code:`simple.csv` correspond to the full reaction network. The :code:`42` 
makes reference to the systematic bias included into the DFT computed energies,
specifically :code:`4.2 kcal/mol` which in kJ is :code:`17.56 kJ/mol`.

Preliminary steps
.................

The first step is to run the microkinetic simulation. For this task we only 
require to have installed the python libraries :code:`numpy` and :code:`scipy`, 
(one of the main design features of **pykinetic** is the generation of 
standalone scripts that do not require the pykinetic to run). 

After ensuring that we have numpy and scipy installed, we now proceed to run the 
simulation:

.. code:: shell-session

   $ python kinetic_model.py

This will generate a :code:`kinetic_model.data` file in 2-6 mins depending on the 
CPU performance of the computer. 


Generation of the network graphs
................................

Next, we proceed to generate the reaction network, colored by concentration of 
the different species at different times during the simulation. For the example
the :code:`simple.csv` files will be used but the files for the full network can
also be used.

.. highlight:: python 

.. literalinclude:: ../../../../examples/example_imine_kinetic/generate_kinetic_snapshots.py

.. highlight:: default

.. code:: shell-session

   $ python generate_kinetic_snapshots.py comps_draco_42_simple.csv reactions_draco_42_simple.csv kinetic_model.data

.. todo::

   Add explanation of the script, or reference to the appropriate python API 
   example and update the python script to use namedtuple._replace method

This will generate 2 :code:`.dot` files, :code:`snapshot_00600.dot` and 
:code.`snapshot_02400.dot`. The following step is to use graphviz to render the images: 

.. code:: shell-session

   $ dot -Tpng snapshot_00600.dot -o figure_7a.png
   $ dot -Tpng snapshot_02400.dot -o figure_7b.png


An animation of the kinetic evolution
-------------------------------------

The files required for the generation of the reaction networks of the imine 
condensation example of the rNets' article can be found in the 
:code:`examples/example_imine_kinetic` folder. This folder contains the following
files: 

.. code:: none

   example_imine_kinetic
    -README.txt
    -comps_draco_42.csv
    -reactions_draco_42.csv
    -comps_draco_42_simple.csv
    -reactions_draco_42_simple.csv
    -kinetic_model.py
    -kinetic_model.index
    -generate_kinetic_snapshots.py
    -generate_kinetic_gif.py

For a detailed explanation of the purpose of each of this files please look at 
the previous section. The focus of this section is to generate a gif changing 
the color of the species as the kinetic simulation progresses. 

Preliminary steps
.................

The first step is to run the microkinetic simulation. For this task we only 
require to have installed the python libraries :code:`numpy` and :code:`scipy`, 
(one of the main design features of **pykinetic** is the generation of 
standalone scripts that do not require the pykinetic to run). Finally to 
generate the final :code:`.gif` we will require a software to merge together 
all the frames, for this example **GIMP** or **imagemagick** are recommended.  

After ensuring that we have numpy and scipy installed, we now proceed to run the 
simulation:

.. code:: shell-session

   $ python kinetic_model.py

This will generate a :code:`kinetic_model.data` file in 2-6 mins depending on the 
CPU performance of the computer. 

GIF generation
..............

To generate a GIF file showing the evolution of the species over time we will
start by generating a :code:`.dot` file for every 10s of simulation into a 
folder named :code:`gif_folder`. To preform this task the python script 
:code:`generate_kinetic_gif.py` is included. 

.. highlight:: python 

.. literalinclude:: ../../../../examples/example_imine_kinetic/generate_kinetic_gif.py

.. highlight:: default

To use it we need to provide the compounds and reactions files and the data from the 
kinetic simulation: 

.. code:: shell-session
   
   $ python generate_kinetic_gif.py comps_draco_42.csv reactions_draco_42.csv kinetic_model.data

.. todo::

   Add explanation of the script, or reference to the appropriate python API 
   example and update the python script to use namedtuple._replace method

Our next step is to transform all the generated :code:`dot` files into 
:code:`png` format. We can do that manually or we can use some bash scripting. 
The following command will work in a bash shell: 

.. code:: shell-session

   $ for dotfile in gif_folder/*.dot; do dot -Tpng $dotfile -o ${dotfile%.*}.png; done

Finally we need to convert all the :code:`.png` files into an animated gif. Specifically 
for the manuscript, the `GIMP <https://www.gimp.org/>` software was used for this task. 
An alternative through command line is imagemagick which can provide a 
decent-quality gif using the following command: 

.. code:: shell-session

   $ convert -delay 0 -loop 1 gif_folder/*.png imine_graph_animation.gif

Upon successfull completion of the '.png' to '.gif' the imine_graph_animation.gif will 
contain the desired gif file. 