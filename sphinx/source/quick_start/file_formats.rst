============
File Formats
============

To simplify the creation of the reaction network rNets relies on the CSV format
which is a tabular format that can be easily created using your preferred 
spreadsheet software or even a plain text editor. 

.. warning:: 
   
   CSV stands for Comma Separated Values, and rNets assumes that convention. 
   Some spreadsheet sofware may provide the option of using a different 
   character for separating the values. Please note that providing a non-comma 
   separated file as input for rNets may lead to errors or bad results. 

Compounds File
--------------

The compounds file requires 5 different colummns: 

*  :code:`name` Corresponds to the text label to uniquely identify the species
*  :code:`energy` Corresponds to the absolute or relative energy of the species. 
   Typically the free energy.  
*  :code:`fflags` b, whatever it is. 
*  :code:`visible` This column allows to hide certain compounds to simplify the 
   final graph, however these hidden compounds are still considered when the 
   normalization is carried out. To hide a compound add :code:`f`.  
*  :code:`opts` Whatever it is 

.. todo:: 
   
   Fill in the descriptions of fflags and opts


Reactions Files
---------------

rNets does not allow the inclusion of tri-molecular reactions, as such the 
maximum number of reactants or products is 2. This constraint is enforced in the 
reactions file, which requires 8 different colummns: 

*  :code:`cleft` Text label of the first reactant
*  :code:`cleft` Text label of the second reactant or empty.  
*  :code:`cright` Text label of the first product. 
*  :code:`cright` Text label of the second product or empty. 
*  :code:`energy` Absolute energy of the TS connecting reactants and products.
   Used to compute the energy barrier. 
*  :code:`direction` Direction of the reaction. :code:`<->` for reversible 
   reactions and `->` for irreversible reactions. 
*  :code:`name` Text identifier of the reaction, typically R0,R1,R2 ...
*  :code:`visible` This column allows to hide certain reactions with a similar 
   effect as hiding compounds.

.. todo::

    more details