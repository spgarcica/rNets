============
File Formats
============

To simplify the creation of the reaction network rNets relies on the CSV format
which is a tabular format that can be easily created using your preferred 
spreadsheet software or even a plain text editor. There are two types of files 
that are required, namely the "Compounds" file and the "Reactions" file. These 
files have multiple columns, where the column name may be repeated, and only a 
subset of all possible columns is required.  

.. warning:: 
   
   CSV stands for Comma Separated Values, and rNets assumes that convention. 
   Some spreadsheet sofware may provide the option of using a different 
   character for separating the values. Please note that providing a non-comma 
   separated file as input for rNets may lead to errors or bad results. 

Compounds File
--------------

The compounds file contains the individual entries of each species in the 
reaction network. Each entry must consist at least of a name, a text 
representation of the compound, and an energy. Below we have an example of how 
the compounds file may look like: 

.. code:: none

   name,energy
   reactant,0
   intermediate,0
   product,0

Here we have three species :code:`reactant`, :code:`intermediate` and 
:code:`product`. In this case the energy of all of them is :code:`0`

Required columns
................

*  :code:`name` Corresponds to the text label to uniquely identify the species.
   It is the text that will show in the generated graph to represent the compound.
*  :code:`energy` Corresponds to the absolute or relative energy of the species. 
   Typically the free energy.

Optional columns
................

*  :code:`fflags` The format of the text for name, there are four possible options:
   :code:`b` ( Bold ), :code:`i`( italics ), :code:`u` ( underlined ) or if it 
   is not specified it will be without any format. 
*  :code:`visible` This column allows to hide certain compounds to simplify the 
   final graph, however these hidden compounds are still considered when the 
   normalization is carried out. To hide a compound add :code:`f`, to reduce 
   its visibility but still show it :code:`grey` and to show the node use 
   :code:`v` (although it is the default behavior so not specifying any other 
   value will default to this option).   
*  :code:`opts` This allows to add more specific graphviz node attributes. 
   these can be found in graphviz `docs <https://graphviz.org/docs/nodes/>`__
   typically they are specified as :code:`"key=value"` where :code:`key` is the 
   attribute, i.e. image, and the :code:`value` is the value that the attribute
   will take for that node, i.e. path/to/my/beautiful.png.   

.. note:: 
   
   Hidden compounds (entries with an :code:`f` value in the :code:`visibility`
   column) are considered in for normalizing the color scale but are not shown 
   in the graph. 

.. warning::

   Although :code:`opts` allows a large degree of customization through graphviz
   please note that the default format of the nodes is specified with html, thus
   it is discouraged for beginner-level users to use this option. 

Reactions File
--------------

The reactions file contains one reaction entry per row. The reaction may be 
unidirectional or bidirectional. The reactions are defined by the compounds that
are involved, thus the same :code:`name` values defined in the compounds file
should be used. Below we have an example of how the reactions file may look like:

.. code:: none

   cleft,cright,direction,name,visible
   reactant,,intermediate,,0.5,<->,R0,
   intermediate,,product,,0.4,<->,R1,


Required columns
................

*  :code:`cleft` Text label of the first reactant.
*  :code:`cright` Text label of the first product. 

At least 1 :code:`cleft` and 1 :code:`cright` must be specified. A second column
:code:`cleft` or :code:`cright` is also accepted, which allows specifying 
bimolecular reactions, but this second column is optional. An example of 
a reactions file containing a bimolecular reaction is shown below: 

.. code:: none

   cleft,cright,cright,direction,name,visible
   reactant,,intermediate,,0.5,<->,R0,
   intermediate,,product1,product2,0.4,<->,R1,


Optional columns
................

*  :code:`energy` Absolute energy of the TS connecting reactants and products.
   Used to compute the energy barrier. 
*  :code:`direction` Direction of the reaction. :code:`<->` for reversible 
   reactions and :code:`->` for irreversible reactions. 
*  :code:`name` Text identifier of the reaction, typically R0,R1,R2 ... It does 
   not have any effect in the produced graph, but may be used as a guide by the 
   user when preparing/editing the files for complex reaction networks.
*  :code:`visible` This column allows to hide certain reactions with a similar 
   effect as hiding compounds. To hide a reaction add :code:`f`, to reduce 
   its visibility but still show it :code:`grey` and to show the node use 
   :code:`v` (although it is the default behavior so not specifying any other 
   value will default to this option).
*  :code:`opts` This allows to add more specific graphviz edge attributes. 
   these can be found in graphviz `docs <https://graphviz.org/docs/edges/>`__
   typically they are specified as :code:`"key=value"` where :code:`key` is the 
   attribute and the :code:`value` is the value that the attribute
   will take for that edge. 

.. note::
   
   rNets does not allow the inclusion of tri-molecular reactions, as such the 
   maximum number of reactants is 2 and the same for the number of products is 2. 
