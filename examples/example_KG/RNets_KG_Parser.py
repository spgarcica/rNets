import numpy as np
import argparse
import rdflib
import owlready2 as owl


hartree_to_eV = 27.2114
hartree_to_kcalmol = 627.509

def gen_edge(nd_list):
    '''Generation of a comma-separated string from a list of nodes
    Input:
    - nd_list. List of strings defining a pair of nodes. If only one (monomolecular reaction)
    is present, add a empty string
    Output:
    Comma-separated string with node pair.
    '''
    if len(nd_list) < 2:
        nd_list.append("")
    return "%s,%s," % tuple(nd_list)

class QueryCore:
    '''Basic class to handle SPARQL query generation at the Python level, defining strings and list
    of strings for different SPARQL statements'''
    def __init__(self,select=None,where=[],prefix={},after=[]):
        # Definition of basic attributes: SELECT (string) and WHERE (list of strings) statement information,
        # namespace prefixes (dict mapping prefix to URI) and possible additional clauses after selection (list)
        self.Select = select
        self.Where = where
        self.Prefix = prefix
        self.After = after
        # Definition of basic namespaces for OntoRXN and Gainesville Core
        self.QueryNamespaces = {"rxn":"http://www.semanticweb.com/OntoRxn#",
                                "gc":"http://purl.org/gc/"}

    def set_prefix_statement(self):
        # Define the prefix block
        prefix_block = ""
        for key,ns in self.Prefix.items():
            ns_string = "PREFIX %s: <%s>\n" % (key,ns)
            prefix_block += ns_string
        self.PrefixString = prefix_block
        return prefix_block

    def set_where_statement(self):
        # Define the WHERE block from a list of statements
        where_statement = " .\n".join(self.Where)
        where_block = "WHERE {\n%s\n}\n" % where_statement
        self.WhereString = where_block
        return where_block

    def set_select_statement(self):
        # Define the SELECT block, including the WHERE part
        where_block = self.set_where_statement()
        select_block = "SELECT %s %s" % (self.Select,self.WhereString)
        self.SelectString = select_block
        return select_block

    def set_after_statement(self):
        # Define the final block with GROUPBY, ORDERBY or other post-processing clauses
        after_block = "\n".join(self.After)
        self.AfterString = after_block
        return after_block
    
    def string_builder(self):
        # Build a string for the SPARQL query from defined attributes. 
        sparql_string = ""
        if (self.Prefix):
            sparql_string += self.set_prefix_statement()
        # SELECT and WHERE must be present: do a sanity check before building the structure
        # which is SELECT select-clauses WHERE { where_clauses }
        if (not self.Select or not self.Where):
            return None
        sparql_string += self.set_select_statement()
        # Add additional statements if present
        if (self.After):
            sparql_string += self.set_after_statement()
        return sparql_string

    def count_args(self,arg_type=None):
        # Count the number of optional string arguments in a given string
        if (not arg_type):
            clause = str(self)
        else:
            clause = getattr(self,arg_type)
        Nargs = clause.count("%s")
        return Nargs

    def pass_args_clause(self,clause,arglist):
        # Pass necessary arguments to the clause and remove them from the input list
        Nargs = clause.count("%s")
        if (Nargs > 0):
            pass_args = arglist[:Nargs]
            clause = clause % tuple(pass_args)
            arglist[:] = arglist[Nargs:]
        return clause
    
    def pass_args(self,arg_list):
        # Convenience function to use command-line arguments to generate SPARQL block
        Nargs = self.count_args()
        if (Nargs != len(arg_list)):
            print("%d args passed, required %d" % (len(arg_list),Nargs))
            return None
        # Check Select, Where and After clauses
        self.Select = self.pass_args_clause(self.Select,arg_list)
        self.Where = [self.pass_args_clause(where_clause,arg_list) for where_clause in self.Where]
        self.After = [self.pass_args_clause(after_clause,arg_list) for after_clause in self.After]
        return self

    def get_results(self,rdf_database,attributes=None,subst={}):
        '''Get the requested attributes from a query.
        Input:
        - rdf_database. RDFLib graph to do the query on.
        - attributes. List of strings with the labels to be extracted from query results, with the
        same name as the variables in SPARQL.
        - subst. Dict of tuples for regex-based substitutions on query results, key-ed by
        attribute names, with first value element being the pattern to find and the second the substitution
        '''
        qr = rdf_database.query(str(self))
        if (not attributes):
            # use all by default and assign to a property
            attributes = [item.toPython().replace("?","") for item in qr.vars]
            self.CurrentAttr = attributes
            
        result_table = []
        for row in qr:
            raw_data = [getattr(row,attr) for attr in attributes]
            # Using the .toPython() function to keep typing
            data = [entry.toPython() if entry else entry for entry in raw_data]
            clear_flag = [attr in subst.keys() for attr in attributes]
            clean_data = [re.sub(*subst[attributes[ii]],entry) if clear_flag[ii] else entry
                          for ii,entry in enumerate(data)]
            result_table.append(tuple(clean_data))
        return result_table
    
    def results_to_dict(self,result_table,attributes):
        # Groups results to a list of dicts, mapping attribute names to their values
        if (not attributes):
            attributes = self.CurrentAttr
        result_dict_table = [OrderedDict(zip(attributes,entry)) for entry in result_table]
        return result_dict_table

    def get_hierarchical_results(self,rdf_database,attributes=None,subst={}):
        result_table = self.get_results(rdf_database,attributes,subst)
        result_dict_table = self.results_to_dict(result_table,attributes)
        return result_dict_table
        
    def __str__(self):
        '''Wrapper to call self.string_builder() if the str built-in is used'''
        return self.string_builder()



class SimpleKGManager:
    '''Base class to manage knowledge graphs and simplify namespace handling and RDFLib-based
    World manipulation to enable SPARQL queries.'''
    def __init__(self,KG_file):
        self.Namespace = {}
        self.load_KG(KG_file)
        self.process_onto()
        
    def load_KG(self,KG_filename):
        ''' Function to load a OntoRXN-based knowledge graph from a local file, handling imports and
        the corresponding RDFLib-compatible world.
        Input:
        - KG_filename. String, name of the file to be read.'''
        owl.onto_path.append("")
        # Instantiate a new world
        onto_world = owl.World()
        ontology = onto_world.get_ontology(KG_filename).load(only_local=True)
        self.Ontology = ontology
        self.MainWorld = onto_world.as_rdflib_graph()
        return None
    
    def process_onto(self):
        '''Basic processing for OntoRXN (clean ontology or instantiated graphs): prepare imports,
        namespaces and RDFLib world'''
        owl.set_datatype_iri(float, "http://www.w3.org/2001/XMLSchema#float") 
        # Prepare namespaces
        namespace_dict = {
            "gc":self.Ontology.get_namespace("http://purl.org/gc/"),
            "osp":self.Ontology.get_namespace("http://theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#"),
            "pt":self.Ontology.get_namespace("http://www.daml.org/2003/01/periodictable/PeriodicTable.owl"),
            "term":self.Ontology.get_namespace("http://purl.org/dc/terms/"),
            "qudt":self.Ontology.get_namespace("http://data.nasa.gov/qudt/owl/qudt#"),
            "occ":self.Ontology.get_namespace("http://theworldavatar.com/ontology/ontocompchem/ontocompchem.owl#"),
            "onto":self.Ontology
        }
        self.Namespace.update(namespace_dict)
        return None

class KinQueryHandler:
    '''Class to store and manage the SPARQL queries required to retrieve essential information from the graph:
    connectivity (steps), mapping between stages and calculations, and mapping between calculations and their properties'''
    def __init__(self,KG=None):
        self.KG = KG
        self.StepQuery = QueryCore()
        self.StageQuery = QueryCore()
        self.CalcQuery = QueryCore()
        # And automatically define all queries
        self.set_step_query()
        self.set_stage_query()
        self.set_calc_query()

        
    def set_query(self,query,select_clause,where_clause,after_clause=[]):
        query.Select = select_clause
        query.Where = where_clause
        query.After = after_clause
        query.Prefix = query.QueryNamespaces
        return query
        
    def set_step_query(self):
        # 1st query: retrieve all steps, the corresponding TS stage (if present) and the node stages
        select_clause = """DISTINCT ?stepX ?stgX
                            ?stgTS
                            (GROUP_CONCAT(?spcName ; separator='+') as ?spcNode)""" 
        where_clause = ["?stepX rxn:hasNode ?stgX",
                        "?stgX rxn:hasSpecies ?spcX",
                        "?spcX rxn:hasCalculation ?calcX",
                        "?calcX rxn:hasAnnotation ?noteX",
                        "BIND(STRBEFORE(?noteX,';') AS ?spcName)",
                        "OPTIONAL{?stepX rxn:hasTS ?stgTS}",
                        ]
        after_clause = ["GROUP BY ?stepX ?stgX ?stgTS","ORDER BY ?stepX"]
        self.set_query(self.StepQuery,select_clause,where_clause,after_clause)
        return self.StepQuery

    def set_stage_query(self):
        select_clause = "DISTINCT ?stgX ?nameX (GROUP_CONCAT(?calcX ; separator=';') AS ?calcList)"
        where_clause = ["?stgX rxn:hasSpecies ?spcX",
                    "?spcX rxn:hasCalculation ?calcX",
                    "OPTIONAL {?stgX rxn:hasAnnotation ?nameX}"
                    ]
        after_clause = ["GROUP BY ?stgX","ORDER BY ?stgX"]
        self.set_query(self.StageQuery,select_clause,where_clause,after_clause)
        return self.StageQuery

    def set_calc_query(self):
        select_clause = "DISTINCT ?calcX ?Eel ?G ?spcName"
        where_clause = [
                    "?calcX gc:hasResult / rxn:hasElecEnergy / gc:hasValue ?Eel",
                    "?calcX gc:hasResult / rxn:hasGibbsFreeEnergy / gc:hasValue ?G",
                    "?calcX rxn:hasAnnotation ?noteX",
                    "BIND(STRBEFORE(?noteX,';') AS ?spcName)"
                    ]

        self.set_query(self.CalcQuery,select_clause,where_clause)
        return self.CalcQuery

    def run_all_queries(self,KG):
        '''Gets results tables for all queries'''
        self.StepTable = self.StepQuery.get_results(KG.MainWorld)
        self.StageTable = self.StageQuery.get_results(KG.MainWorld)
        self.CalcTable = self.CalcQuery.get_results(KG.MainWorld)
        return None

def read_kg_and_query(kg_file):
    '''Directly manages a CRN-KG file and runs the queries expressed in
    KinQueryHandler class, returning these results.
    Input:
    - kg_file. String, name of an OWL file containing a OntoRXN-based knowledge graph
    Output:
    - query_handler. KinQueryHandler object containing information from calculations.'''
    ### Handle the knowledge graph and the queries
    onto_wrap = SimpleKGManager(kg_file)

    ### Management of SPARQL queries with KinQueryHandler class

    query_handler = KinQueryHandler()
    query_handler.run_all_queries(onto_wrap)
    return query_handler

def kin_query_formatter(query_handler):
    '''Convenience function to format the results in a filled KinQueryHandler object to
    dictionaries: mapping stage to a list of calculations, calculations to energies and calculations to names
    Input:
    - query_handler. KinQueryHandler object containing information from calculations.
    Output:
    - stage_to_calcs. Dict mapping stage names to list of calculations.
    - calc_to_name. Dict mapping calculation ids to simplified names.
    - calc_to_gibbs. Dict mapping calculation ids to Gibbs free energies.
    '''

    stage_to_calcs = {entry[0]:entry[-1].split(";") for entry in query_handler.StageTable}
    calc_to_name = {entry[0]:entry[3] for entry in query_handler.CalcTable}
    # Transform kcal mol-1 (example) to electronvolt
    eV_to_kcalmol = 23.060548
    calc_to_gibbs = {entry[0]:entry[2]/eV_to_kcalmol for entry in query_handler.CalcTable}

    return stage_to_calcs,calc_to_name,calc_to_gibbs

def build_rnet_files(query_handler,reference="",hidden_species=[]):
    '''Builds the compound and reaction files for RNets from the reaction set defined in a
    knowledge graph, using a filled KinQueryHandler as input.
    Input:
    - query_handler. KinQueryHandler object containing information from calculations.
    Output:
    - compounds_block. String, contents of the COMPOUNDS file for rNets.
    - reacs_block. String, contents of the REACTIONS file for rNets.
    '''

    stage_to_calcs,calc_to_name,calc_to_gibbs = kin_query_formatter(query_handler)
    name_to_calc = {v:k for k,v in calc_to_name.items()}
    # Go through steps, for every stage retrieve the corresponding nodes
    known_edges = []
    edge_list = []

    for step in query_handler.StepTable:
        if step[0] not in known_edges:
            known_edges.append(step[0])
            # get the species involved in this stage: recall that there might be several (or None)
            stg_ts = step[2]
            stg_ts_calcs = stage_to_calcs.get(stg_ts,[None])
            # locate the node
            stg_nd = step[1]
            stg_nd_calcs = stage_to_calcs[stg_nd]
            edge = [stg_ts_calcs,stg_nd_calcs]
            edge_list.append(edge)
        else:
            idx = known_edges.index(step[0])
            # add the 2nd node
            stg_nd = step[1]
            stg_nd_calcs = stage_to_calcs[stg_nd]
            edge_list[idx].append(stg_nd_calcs)

    # Instead of building a graph, we want to have all species as nodes and the stage-based transition states
    # We also want to compute relative energies
    final_nodes = []
    final_edges = []

    # Check the reference, if present
    e_ref = 0
    if reference:
        reference_calcs = [name_to_calc[spc] for spc in reference.split("+")]
        e_ref = sum([calc_to_gibbs[calc] for calc in reference_calcs])

    for edge in edge_list:
        # Clear up species that are present in both nodes (and possibly the TS) to avoid cluttering the edge
        rep_species = [spc for spc in edge[1] if spc in edge[2]]
        edge_clear = [[spc for spc in ed if spc not in rep_species] for ed in edge]
        # We need the individual nodes
        e_nd1 = sum([calc_to_gibbs[calc] for calc in edge[1]]) - e_ref
        e_nd2 = sum([calc_to_gibbs[calc] for calc in edge[2]]) - e_ref
        nodes_fmt = []
        # Auxiliary species will be assigned zeros
        for jj in range(1,3):
            for calc in edge_clear[jj]:
                name = calc_to_name[calc]
                if name in hidden_species:
                    nodes_fmt.append((name,0))
                else:
                    nodes_fmt.append((name,[e_nd1,e_nd2][jj-1]*hartree_to_kcalmol))

        nodes_fmt_nw = [nd for nd in nodes_fmt if nd not in final_nodes]
        final_nodes.extend(nodes_fmt_nw)
        # Process the TS, which will be an unique edge -> also, attempt to handle barrierless
        # there might be several nodes in a list: join them by a + symbol for consistency
        ndname1 = "+".join([calc_to_name[calc] for calc in edge_clear[1]])
        ndname2 = "+".join([calc_to_name[calc] for calc in edge_clear[2]])
        tsname = calc_to_name.get(edge_clear[0][0],None)
        if not tsname:
            tsenergy = max([e_nd1,e_nd2])
        else:
            tsenergy = sum([calc_to_gibbs[calc] for calc in edge[0]]) - e_ref

        edge_fmt = (ndname1,ndname2,tsname,tsenergy*hartree_to_kcalmol)
        final_edges.append(edge_fmt)

    # And write to files
    header_compounds = "name,energy,fflags,visible,opts\n"
    # Turn off visibility of auxiliary species
    fontsize = 14
    visibility = ["f" if nd[0] in hidden_species else "" for nd in final_nodes]
    compounds = ["%s,%.6f,b,%s," % (nd[0],nd[1],vis) for nd,vis in zip(final_nodes,visibility)]
    compounds_block = header_compounds + "\n".join(compounds) + "\n"

    header_edges = "cleft,cleft,cright,cright,energy,direction,name,visible\n"
    edges_out = []
    for ii,edge in enumerate(final_edges):
        left = gen_edge(edge[0].split("+"))
        right = gen_edge(edge[1].split("+"))
        edges_out.append(left + right + "%.6f,<->,R%d," % (edge[3],ii))

    edges_block = header_edges + "\n".join(edges_out) + "\n"

    return compounds_block,edges_block


def main():
    ### CLI-based arguments
    parser = argparse.ArgumentParser(description="Parse knowledge graphs for visualization")
    parser.add_argument("outfname_comp", type=str, help="Provide the name for the compounds output.")
    parser.add_argument("outfname_rx", type=str, help="Provide the name for the reactions output.")
    parser.add_argument("input_kg", type=str, help="Path to knowledge graph file")

    parser.add_argument("--reference", '-r', type=str, default="",help="Provide the names of the species used as energy reference, separated by +")
    parser.add_argument("--hidden-species", '-hs', type=str, default="",help="Provide the names of species that will be hidden in the graph, separated by commas")

    args = parser.parse_args()

    kq_handler = read_kg_and_query(args.input_kg)
    compounds_block,edges_block = build_rnet_files(kq_handler,args.reference,args.hidden_species.split(","))

    with open(args.outfname_comp,"w") as fout:
        fout.write(compounds_block)

    with open(args.outfname_rx,"w") as fout:
        fout.write(edges_block)

if __name__ == "__main__":
    main()
