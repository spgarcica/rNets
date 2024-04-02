=========
rNets
=========

------------------------------------------------------------------
A python tool for the generation of graphs of reaction network 
------------------------------------------------------------------

.. 
   # commented because these links are for pykinetic, when we have the 
   # updated ones I will uncomment this section 
   image:: https://zenodo.org/badge/DOI/10.5281/zenodo.8053050.svg
   :target: https://doi.org/10.5281/zenodo.8053050

.. project-description-start


rNets is an innovative python tool designed for visualization of reaction 
networks with a simple and robust command-line interface. rNets was conceptualized
with the core principles of modularity, and easy integration with existing 
software packages by reducing dependencies to the minimum. This tool not only 
simplifies the visualization process but also opens new avenues for exploring 
complex reaction networks in diverse research contexts.

.. project-description-end

.. contents:: 
   :backlinks: none
   :depth: 2
   :local:


Getting Started
---------------

These instructions will get you a copy of the project up and running on your
local machine.

.. setup-instructions-start

Prerequisites
.............

- python >= 3.12

Installing the dependencies
...........................

rNets only depends on the python standard library that usually comes with the 
cpython interpreter, the default one adopted by the python community. This means
the the only requisite for installing rNets is python. The python community has 
placed a lot of effort into the documentation and actively maintains it so for 
further instructions on how to install python into your computer we highly 
recommend to check the official 
`python <https://wiki.python.org/moin/BeginnersGuide>`__ documentation.

Although for being able to install and run rNets only python is required, rNets 
relies heavily on graphviz for the actual rendering of the images, as the output
of rNets is tipically a .dot file. Installing graphviz is tipically a 
straightforward and quick process. Graphviz may be downloaded from their 
`official <https://graphviz.org/download/>`__ webpage.

Installing rNets
....................

rNets can be directly installed through pip as a version of the package is 
hosted at the Python Package Index (PyPI): 

.. code:: shell-session

   $ python -m pip install rNets

.. warning:: 

   Warning: The rNets code is not available at the Python Package Index, but 
   will soon be available, please use the other installation options.

However, if the user does prefer it, it can also be easily installed from the 
source code. For that we will start by downloading the source code using git. 

.. code:: shell-session

   $ git clone https://codeberg.org/spgarcica/rNets.git rnets-source

Next we proceed to install it using pip

.. code:: shell-session
   
   $ python -m pip install rnets-source/

If you do not have git or do prefer to download manually the source 
code as a .zip or .tar.gz do it install it. 

.. code:: shell-session

   $ python -m pip install rNets.tar.gz

.. note::

    It is possible to unpack it and install it as indicated in the previous step
    but it is not required. 


Uninstalling rNets
......................

Completely uninstalling rNets is also quite easy due to its lack of dependencies.
All that is needed is to command pip to uninstall the package 

.. code:: shell-session

   $ python -m pip uninstall rNets

.. setup-instructions-end

Developed with
--------------

- python 3.12


Examples and Docs
-----------------

The examples folders contains with corresponding readme files the instructions 
and necessary data to generate a variety of different reaction networks and 
animations.  

The documentation of rNets can be accessed at `<https://spgarcica.github.io/rNets/>`_ .
Here a more detailed description of the examples can also be found. 


Authors
-------

.. project-authors-start

List of main developers and contact emails:  

*  Sergio Pablo-García [
   `ORCID <https://orcid.org/0000-0002-3327-9285>`__ , 
   `Github <https://github.com/spgarcica>`__ ]
*  Raúl Pérez-Soto [
   `ORCID <https://orcid.org/0000-0002-6237-2155>`__ ,
   `Github <https://github.com/rperezsoto>`__ ]
*  Albert Sabadell-Rendón [
   `ORCID <https://orcid.org/0000-0003-2905-1541>`__ ,
   `Github <https://github.com/asabadellr>`__ ] 
*  Diego Garay-Ruiz [
   `ORCID <https://orcid.org/0000-0003-0744-0562>`__ ,
   `Github <https://github.com/dgarayr>`__ ] 
*  Vladyslav Nosylevskyi [
   `ORCID <https://orcid.org/0009-0003-1544-7745>`__ 
   `Github <https://github.com/wvlab>`__ ] 
*  Nuria Lopez [
   `ORCID <https://orcid.org/0000-0001-9150-5941>`__ ] 

.. project-authors-end

License
-------

.. project-license-start

rNets is freely available under an `MIT <https://opensource.org/licenses/MIT>`__ License

.. project-license-end