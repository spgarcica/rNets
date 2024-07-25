This folder contains all the files required to generate the Figure 7 and 
figures S5 and S6: 

a) 'assets/comps_draco_42_simple.csv','assets/reactions_draco_42_simple.csv',
   'assets/comps_draco_42.csv','assets/reactions_draco_42.csv'
b) 'kinetic_model.py', 'assets/kinetic_model.index'
c) 'kinetic_snapshots.py' 
d) 'kinetic_gif.py' 
e) 'run.py'

Files in a) are used to create the reaction network and provide the energetics
needed to compute the kinetic constants and thus the net rates of the 
reactions. Files in b) are files generated using the pykinetic 
software, the '.index' file contains similar information to the 'comps' and 
'reactions' files, to simplify re-creating the input needed for pykinetic. 
The 'kinetic_model.py' contains how to carry out the actual microkinetic 
simulation, and will generate a '.data' file containing the concentrations 
at each time of all species. The file in c) is a script to generate the '.dot'
files at different times, which are used in the generation of the Figure 
7a and 7b of the original rNets publication. The file in d) is a script to 
generate all the .dot files required to generate the .gif file which is the 
focus of the following section. The file in e) integrates all the workflow within
a single script.

.. note::

   The 'kinetic_model.py' obtained from pykinetic (v0.1.0) has been slighly 
   modified to facilitate the re-generation of all figures under the 
   'run.py' script

The files with the termination "simple.csv" include the ones required to 
generate the figures as presented in the manuscript (Figure 7a and 7b). The 
files without the termination "simple.csv" correspond to the full reaction 
network (Used to generate the figure S5 and S6 in the SI). The '42' 
makes reference to the systematic bias included into the DFT computed energies,
specifically 4.2 kcal/mol which in the main document shows as 17.56 kJ/mol.

.. note::
   For convenience, to generate all the figures we provide the run.py 
   script which automates the generation of all the figures (Figure 7a, 7b, S4 and 
   S5) facilitating the reproducibility of the figures in the article across 
   different OS. 

Data preparation
----------------

The first step is to run the microkinetic simulation. For this task we only 
require to have installed the python libraries numpy and scipy, which is one 
of the main features of pykinetic, the generation of standalone scripts that 
do not require the pykinetic to run. To run the simulation we execute: 

python kinetic_model.py

This will generate a 'kinetic_model.data' in file in 2-6 mins depending on the 
CPU performance of the computer. 

Static Figure Generation
------------------------

Next, To illustrate the generation of Figures 7a, 7b, S5 and S6 I will use as example the 
generation of Figures 7a and 7b. First we will execute the following line: 

python kinetic_snapshots.py assets/comps_draco_42_simple.csv assets/reactions_draco_42_simple.csv kinetic_model.data

This will generate 2 .dot files, 'snapshot_00600.dot' and 'snapshot_02400.dot'.
The following step is to use graphviz to render the images: 

dot -Tpng snapshot_00600.dot -o figure_7a.png
dot -Tpng snapshot_02400.dot -o figure_7b.png

In order to generate figures S5 and S6 we should substitute the the *simple.csv files by 
the *_42.csv files, which correspond to the full network. 

GIF generation
--------------

To generate a GIF file showing the evolution of the species over time we will
start by generating a .dot file for every 10s of simulation into a folder named
'gif_folder'. We can preform this task by running the following line: 

python kinetic_gif.py assets/comps_draco_42.csv assets/reactions_draco_42.csv kinetic_model.data

Our next step is to transform all the generated dot files into .png format 
we can do that manually or we can use some bash scripting. The following 
command will work in a bash script: 

for dotfile in gif_folder/*.dot; do dot -Tpng $dotfile -o ${dotfile%.*}.png; done

Finally we need to convert all the '.png' files into an animated gif. Specifically 
for the manuscript, the GIMP software was used for this task. An alternative through
command line is imagemagick which can provide a decent-quality gif using the following
command: 

magick convert -delay 0 -loop 1 gif_folder/*.png imine_graph_animation.gif

.. note::

   for imagemagick versions up to 6 please substitute "magick convert" by "convert"

Upon successfull completion of the '.png' to '.gif' the imine_graph_animation.gif will 
contain the desired gif file. 
