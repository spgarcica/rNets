.. |example_00| graphviz:: ../resources/examples/example_00.dot
.. |example_01| graphviz:: ../resources/examples/example_01.dot
.. |example_02| graphviz:: ../resources/examples/example_02.dot
.. |example_03| graphviz:: ../resources/examples/example_03.dot
.. |example_04a| graphviz:: ../resources/examples/example_04a.dot
.. |example_04b| graphviz:: ../resources/examples/example_04b.dot
.. |example_04c| graphviz:: ../resources/examples/example_04c.dot

=======================
Python API Examples
=======================

In this section we will cover examples using directly the python API interface
instead of the command line. The usage of the python API facilitates the 
integration of python libraries such as pykinetic, which will also be covered
in the examples. 


My first Network
----------------

To introduce the basic components of the python API of rNets we will create 
a very simple reaction network, which is shown below: 

.. centered:: |example_00|

The first thing is importing the appropriate classes. The :code:`Network` class 
is within the struct :code:`struct` module 

.. code:: python 

   from rnets.struct import Network

A network is composed of :code:`Compound` and :code:`Reaction` objects, are also
in the same module

.. code:: python 

   from rnets.struct import Compound, Reaction

Now that we have the basic building blocks we can proceed to define our different
compounds, namely A, B, C and D

.. code:: python 

   A = Compound(name='A',energy=0.0,idx=0) 
   B = Compound('B',1.0,1) 
   C = Compound('C',0.0,2) 
   D = Compound('D',-2.0,3)

Here, the minimal parameters needed to define a compound are: :code:`name`
, :code:`energy`, :code:`idx` . The default energy unit is :code:`eV` so 
according to the previous code, :code:`B` is :code:`1eV` higher in energy than 
:code:`A` while :code:`D` is :code:`2eV` lower in energy. The :code:`idx` value
is used to uniquely identify each compound. This allows more freedom to the 
value of :code:`name` as there are no constraints on the text that can be used. 

After defining the compounds, we can now proceed to define the reactions: 

.. code:: python
   
   reactants = (A,)
   products = (B,) 
   r1 = Reaction(name='r1', 
                 compounds=(reactants,products),
                 energy=4.0,
                 idx=0)
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 

The :code:`name` and :code:`idx` parameters are used to identify the reaction
in an user-friendly and code-friendly, respectively, but have no effect on the 
final representation. The :code:`compounds` parameter is a tuple composed from 
reactants and products, in both cases a tuple containing 1 or more 
:code:`Compounds` . The :code:`energy` corresponds to the energy of the 
transition state corresponding to the reaction. In these examples the transition
states are :code:`20eV` higher than :code:`A` and :code:`C` .

Finally we proceed to create the network: 

.. code:: python 

   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

This is quite straightforward as we have all the pieces together. Putting 
together all the previous code snippets: 

.. code:: python 
   
   from rnets.struct import Network, Compound, Reaction

   A = Compound('A',0.0,0) 
   B = Compound('B',1.0,1) 
   C = Compound('C',0.0,2) 
   D = Compound('D',-2.0,3)

   r1 = Reaction('r1',((A,),(B,)),4.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

As we now have the network created we can proceed to draw the graphs which is 
in the topic of the next two examples. 

Drawing a thermodynamic graph
-----------------------------

For an introduction to the different components of a :code:`Network` please 
check the `My first Network`_

To draw the reaction network we will use the :code:`plotter` module. As in this 
example we will be coloring the nodes based on the energies of the compounds and
the color and thickness of the of the edges based on the barriers, we will 
specifically use the :code:`thermo` submodule. In the `Drawing a kinetic graph`_
we use the :code:`kinetic` instead. 

.. code:: python

   from rnets.plotter.thermo import build_dotgraph

Together with the network generation we have the following code: 

.. code:: python 

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.thermo import build_dotgraph

   A = Compound('A',0.0,0) 
   B = Compound('B',1.0,1) 
   C = Compound('C',0.0,2) 
   D = Compound('D',-2.0,3)

   r1 = Reaction('r1',((A,),(B,)),4.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

Now, we proceed to the generation of the dotfile contents and to write them: 

.. code:: python 

   graph = build_dotgraph(nw)

   with open("example1.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))

After we have generated our :code:`.dot` file all that remains is to transform 
it into an image format, which we can do with any of graphviz's tools. As we 
are doing these examples in python we will use python to call the :code:`dot` 
tool: 

.. code:: python 

   import subprocess
   subprocess.run('dot -Tpng example1.dot -o example1.png',shell=True)

.. centered:: |example_01|

With this we will have generated a basic reaction network completely using rNets' 
python API. Putting all together: 

.. code:: python 

   import subprocess

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.thermo import build_dotgraph

   # Creation of the reaction network
   A = Compound('A',0.0,0) 
   B = Compound('B',1.0,1) 
   C = Compound('C',0.0,2) 
   D = Compound('D',-2.0,3)

   r1 = Reaction('r1',((A,),(B,)),4.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

   # Creation of the graph and saving it as a .dot file. 
   graph = build_dotgraph(nw)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   # Generating a PNG from the created .dot file
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)

Drawing a kinetic graph
-----------------------

For an introduction to the different components of a :code:`Network` please 
check the `My first Network`_

To draw the reaction network we will use the :code:`plotter` module. As in this 
example we will be coloring the nodes based on the energies of the compounds and
the color and thickness of the of the edges based on the barriers, we will 
specifically use the :code:`kinetic` submodule. In the `Drawing a thermodynamic graph`_
we use the :code:`thermo` instead. 

.. code:: python

   from rnets.plotter.kinetic import build_dotgraph

Contrary to the `Drawing a thermodynamic graph`_ example, here it is needed to 
modify the creation of the network, as we need to provide information about the 
concentrations of each compound. The units of the concentrations have to be 
consistent with the energy units, since the rates of the reactions will be 
computed based on the energies and concentrations. 

.. code:: python 

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.kinetic import build_dotgraph

   A = Compound('A',0.0,0,conc=0.75) 
   B = Compound('B',1.0,1,conc=0.1) 
   C = Compound('C',0.0,2,conc=1.0) 
   D = Compound('D',-2.0,3,conc=0.25)

   r1 = Reaction('r1',((A,),(B,)),4.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

.. note:: 

   For the example we are going to use arbitrary numbers, but these numbers can 
   be read from an existing file containing the output of a kinetic simulation 
   software.

Now, we proceed to the generation of the dotfile contents and to write them: 

.. code:: python 

   graph = build_dotgraph(nw)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))

After we have generated our :code:`.dot` file all that remains is to transform 
it into an image format, which we can do with any of graphviz's tools. As we 
are doing these examples in python we will use python to call the :code:`dot` 
tool: 

.. code:: python 

   import subprocess
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)

.. centered:: |example_02|

With this we will have generated a basic reaction network completely using rNets' 
python API. Putting all together: 

.. code:: python 

   import subprocess

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.kinetic import build_dotgraph

   # Creation of the reaction network
   A = Compound('A',0.0,0,conc=0.75) 
   B = Compound('B',1.0,1,conc=0.1) 
   C = Compound('C',0.0,2,conc=1.0) 
   D = Compound('D',-2.0,3,conc=0.25)

   r1 = Reaction('r1',((A,),(B,)),4.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

   # Creation of the graph and saving it as a .dot file. 
   graph = build_dotgraph(nw)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   # Generating a PNG from the created .dot file
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)



Using different energy units or temperature
-------------------------------------------

In this example we will get introduced to the chemical configuration class
( :code:`rnets.chemistry.ChemCfg` ). to illustrate its usage we will borrow the 
`Drawing a kinetic graph`_ example. 

First we will add to the imports the Chemcfg

.. code:: python 
   
   import subprocess

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.kinetic import build_dotgraph
   from rnets.chemistry import ChemCfg


Next, we are going to define our reaction network in :code:`kcal/mol` 

.. code:: python 

   A = Compound('A',0.0,0,conc=0.75)                  # 0.0 eV
   B = Compound('B',23.1,1,conc=0.1)                  # 1.0 eV
   C = Compound('C',0.0,2,conc=1.0)                   # 0.0 eV
   D = Compound('D',-46.1,3,conc=0.25)                # -2.0 eV

   r1 = Reaction('r1',((A,),(B,)),92.2,0)    # 4.0 eV 
   r2 = Reaction('r2',((B,C),(D,)),161.4,1)  # 7.0 eV

   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

The next step is to instantiate our chemical configuration object.

.. code:: python 

   chem_cfg = ChemCfg(e_units='kcal/mol')

If the energies provided were at a reference state of 500K it is also specified 
at the chemical configuration: 

.. code:: python 

   chem_cfg = ChemCfg(e_units='kcal/mol',T=500)

Now, we proceed to the generation of the dotfile using the 
:code:`kinetic.build_dotgraph` function. Here we need to specify as a parameter 
of the function the chemical configuration object. 

.. code:: python 

   graph = build_dotgraph(nw,chem_cfg=chem_cfg)

Finally, we proceed as in the other examples to write the :code:`.dot` file and 
transform it to a :code:`.png` 

.. code:: python 

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)

.. centered:: |example_03|

When we put all the steps together we end up with the following code: 

.. code:: python 

   import subprocess

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.kinetic import build_dotgraph
   from rnets.chemistry import ChemCfg 

   # Creation of the reaction network
   A = Compound('A',0.0,0,conc=0.75)                  # 0.0 eV
   B = Compound('B',23.1,1,conc=0.1)                  # 1.0 eV
   C = Compound('C',0.0,2,conc=1.0)                   # 0.0 eV
   D = Compound('D',-46.1,3,conc=0.25)                # -2.0 eV

   r1 = Reaction('r1',((A,),(B,)),92.2,0)    # 4.0 eV 
   r2 = Reaction('r2',((B,C),(D,)),161.4,1)  # 7.0 eV
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

   # Creation of the Chemical Configuration
   chem_cfg = ChemCfg(e_units='kcal/mol')

   # Creation of the graph and saving it as a .dot file. 
   graph = build_dotgraph(nw)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   # Generating a PNG from the created .dot file
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)


Formatting our graph
--------------------

In this example we will get introduced to the Graph, Edge and Node configuration
classes ( :code:`rnets.plotter.utils.GraphCfg` , 
:code:`rnets.plotter.utils.EdgeCfg` and :code:`rnets.plotter.utils.NodeCfg`). 
To illustrate their usage we will borrow the `Drawing a kinetic graph`_ example 
and we will change the width of the edges as well as the colorscheme.

.. note:: 

   In the following examples, only the :code:`GraphCfg` and :code:`EdgeCfg` 
   classes will be used, however the usage of :code:`NodeCfg` is similar 
   to :code:`EdgeCfg` .

First we will add to the imports the :code:`GraphCfg` and :code:`EdgeCfg` classes:  

.. code:: python 
   
   import subprocess

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.kinetic import build_dotgraph
   from rnets.plotter.utils import GraphCfg, EdgeCfg


Next, we are going to define our reaction network 

.. code:: python 

   A = Compound('A',0.0,0,conc=0.75) 
   B = Compound('B',1.0,1,conc=0.1) 
   C = Compound('C',0.0,2,conc=1.0) 
   D = Compound('D',-2.0,3,conc=0.25)

   r1 = Reaction('r1',((A,),(B,)),4.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

The next step is to instantiate our edge configuration object.

.. code:: python 

   edge_cfg = EdgeCfg(width=3)

First, we will generate the graph without changing the colorscheme which is a 
format of the graph, but we still need to create a :code:`GraphCfg` object, to 
include our :code:`EdgeCfg` object: 

.. code:: python 

   graph_cfg = GraphCfg(edge=edge_cfg)

and proceed to generate our graph, dotfile and png as in the previous examples: 

.. code:: python 

   graph = build_dotgraph(nw,graph_cfg=graph_cfg)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)

.. centered:: |example_04a|

Second, if we also want to change the color scheme, we need to specify it when 
we create the :code:`GraphCfg` object. all we will need to do is to 
specify a sequence of floats. The default colorscheme is :code:`viridis` which 
is pre-defined in :code:`rnets.colors.colorschemes.VIRIDIS` . Here we can 
find other pre-defined colorschemes such as :code:`magma`, :code:`plasma`, 
:code:`inferno` and :code:`cividis` (All in uppercase). To use a pre-defined 
color scheme the easiest will be to import it: 

.. code:: python

   from rnets.colors import PLASMA

Now we instantiate the :code:`GraphCfg` object

.. code:: python 

   graph_cfg = GraphCfg(edge=edge_cfg,colorscheme=PLASMA)

And the remaining steps are the same ones as before: 

.. code:: python 

   graph = build_dotgraph(nw,graph_cfg=graph_cfg)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)

.. centered:: |example_04b|

If instead we want to define our own colorscheme, we need to specify a sequence 
of colors, represented as tuples of :code:`RGB` values between 0 and 1. For 
convenience when defining custom colorschemes, we can find a dictionary with 
some name to RGB tuple mapping at :code:`rnets.colors.palettes` that we can use: 

.. code:: python 

   from rnets.colors.palettes import css as colorname_to_rgb

   my_colorscheme = ['magenta','limegreen']
   colorscheme = [colorname_to_rgb[name] for name in my_colorscheme]

As we did before, we now define our :code:`GraphCfg` object with our custom 
colorscheme and proceed to generate the graph, :code:`.dot` file and 
:code:`.png`

.. code:: python 

   graph_cfg = GraphCfg(edge=edge_cfg,colorscheme=colorscheme)

   graph = build_dotgraph(nw,graph_cfg=graph_cfg)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)

.. centered:: |example_04c|

When we put all the steps together we end up with the following code: 

.. code:: python 

   import subprocess

   from rnets.struct import Network, Compound, Reaction
   from rnets.plotter.kinetic import build_dotgraph
   from rnets.plotter.utils import GraphCfg, EdgeCfg
   from rnets.colors.colorschemes import PLASMA

   # Creation of the reaction network
   A = Compound('A',0.0,0,conc=0.75) 
   B = Compound('B',1.0,1,conc=0.1) 
   C = Compound('C',0.0,2,conc=1.0) 
   D = Compound('D',-2.0,3,conc=0.25)

   r1 = Reaction('r1',((A,),(B,)),4.0,0) 
   r2 = Reaction('r2',((B,C),(D,)),7.0,1) 
   
   nw = Network(compounds=(A,B,C,D),reactions=(r1,r2))

   # Formatting
   edge_cfg = EdgeCfg(width=3)
   graph_cfg = GraphCfg(edge=edge_cfg,colorscheme=PLASMA)

   # Creation of the graph and saving it as a .dot file. 
   graph = build_dotgraph(nw,graph_cfg=graph_cfg)

   with open("example.dot", 'w', encoding="utf8") as of:
       of.write(str(graph))
   
   # Generating a PNG from the created .dot file
   subprocess.run('dot -Tpng example.dot -o example.png',shell=True)

Integration with other software: Pykinetic (thermo)
---------------------------------------------------

.. note::
   
   Currently under construction:
   An example of how to adapt pykinetics classes to generate a thermodynamic graph

Integration with other software: Pykinetic (kinetic)
----------------------------------------------------

.. note::
   
   Currently under construction:
   An example of how to adapt pykinetics classes to generate a kinetic graph
