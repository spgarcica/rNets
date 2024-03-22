============
Installation
============

These instructions will get you a copy of the project up and running on your
local machine.

Prerequisites
-------------

- python >= 3.12

Installing the dependencies
---------------------------

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
----------------

rNets can be directly installed through pip as a version of the package is 
hosted at the Python Package Index (PyPI): 

.. code:: shell-session

   $ python -m pip install rNets

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
------------------

Completely uninstalling rNets is also quite easy due to its lack of dependencies.
All that is needed is to command pip to uninstall the package 

.. code:: shell-session

   $ python -m pip uninstall rNets

Developed with
--------------

- python 3.12