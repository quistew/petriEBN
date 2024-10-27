import re
import networkx as nx
import graphviz as gv
import pydot
import networkx as nx
import MultiQM
import table_conversion_for_EG as Convert
import table_from_dsgrn as Table

BOOL_AND = 'AND'

class ExpandedGraph:
    def __init__(self, edges):
        """
        Initialize the ExpandedGraph with given edges.
        
        Args:
            edges (dict): A dictionary where keys are nodes and values are lists of successor nodes.
        """
        self.edges = edges
        self.virtual_nodes, self.composite_nodes = self._identify_nodes()
        
    def _identify_nodes(self):
        """Identify and separate virtual and composite nodes."""
        virtual_nodes = {n: [] for n in self.edges if BOOL_AND not in n}
        composite_nodes = {}

        for n2, successors in self.edges.items():
            if n2 not in composite_nodes:
                composite_nodes[n2] = []
                if BOOL_AND not in n2:
                    composite_nodes[n2].append(n2)

            for n1 in successors:
                if BOOL_AND in n1:
                    composite_nodes.setdefault(n1, []).append(n2)
                else:
                    if n2 not in virtual_nodes[n1]:
                        virtual_nodes[n1].append(n2)
                
        return virtual_nodes, composite_nodes

    def get_virtual_and_composite_nodes(self):
        """Return virtual and composite node dictionaries."""
        return self.virtual_nodes, self.composite_nodes


def add_node_to_dict(node_state_combo, node, sister_nodes, edge_dict):
    if node not in edge_dict:
            edge_dict[node] = [node_state_combo]
    else:
        if node_state_combo not in edge_dict[node]:
            edge_dict[node].append(node_state_combo)

    for sister_node in sister_nodes:
        if sister_node not in edge_dict:
            edge_dict[sister_node] = []
        if sister_node in node and sister_node != node:
            if node not in edge_dict[sister_node]:
                edge_dict[sister_node].append(node)


def convert_qm_function_to_dict(node_state_combo, function, sister_nodes, edge_dict = {}):
    '''node_state_combo : str - the label of the node and state of the function, 
                          for example if node = A and state = 0 then node_state_combo = A$0
       function : output of MultiQM.qm(function, fullnodelist, fullnodestates) 
    '''

    ORs = [0]
    ORs += [m.start() for m in re.finditer(' OR ', function)] # finding all nodes
    ORs += [-1]

    if ORs == [0, -1]:  # i.e., if the function doen't have OR clauses
        node = function[1:-1] # remove parathensis
        add_node_to_dict(node_state_combo, node, sister_nodes, edge_dict)

    else: # i.e., if the function does have OR clauses
        for i in range(len(ORs)-1):
            if i == 0:
                node = function[ORs[i]+1:ORs[i+1]-1]
                #print('n1', i, node)
            if i == len(ORs)-2:
                node = function[ORs[i]+5:-1]
                #print('n2', i, node)
            if i in range(1,len(ORs)-2):
                node = function[ORs[i]+5:ORs[i+1]-1] # removing ' OR '
                #print('n3', i, node)
            
            add_node_to_dict(node_state_combo, node, sister_nodes, edge_dict)
               
    return edge_dict

def convert_dict_to_nx(dict):
    G = nx.DiGraph()
    attr = {}
    for node in dict:
        G.add_node(node)
        if node.count('$')>1:
            attr[node] = 1
        else:
            attr[node] = 0
        for edge in dict[node]:
            G.add_edge(node, edge)
    nx.set_node_attributes(G,attr,name = 'c')
    return G

def obtain_EG_edges(node_states, functions):
    sister_nodes = [node+'$'+str(state) for node in node_states for state in node_states[node]]
    edge_dict_new = {}
    for node_state_combo in functions:
        edge_dict = edge_dict_new
        function = functions[node_state_combo]
        edge_dict_new = convert_qm_function_to_dict(node_state_combo, function, sister_nodes, edge_dict)

    return edge_dict

def render_EG_as_png(edge_dict, filename):
      EG = convert_dict_to_nx(edge_dict)
      nx.drawing.nx_pydot.write_dot(EG, filename)
      gv.render('dot', 'png', filename)

def obtain_BCF_functions(network_string,pgi,node_states):
    edges = Table.obtain_network_edges(network_string)
    params = Convert.obtain_param_as_table(network_string, pgi)
    fullnodelist = list(node_states.keys())
    fullnodestates = list(node_states.values())
    functions = {}

    for node in fullnodelist:
        for state in node_states[node]:
            node_state_combo = node + '$' + str(state)
            function = ''
            if node in params:
                for b in params[node]:
                    if b[-1] == state:
                        comp_node = '('
                        for i in range(len(b[:-1])):
                            comp_node = comp_node+edges[node][i][0]+'$'+str(b[i])
                            if i != len(b[:-1])-1:
                                comp_node = comp_node+' AND '
                            else:
                                comp_node = comp_node+')'
                                #print(node,b,comp_node)
                        if function == '':
                            function = function + comp_node
                        else:
                            function = function + ' OR '+comp_node
            if function != '':
                BCF = MultiQM.qm(function, fullnodelist, fullnodestates)
                if BCF != '1':
                    functions[node_state_combo] = BCF
                else:
                    functions[node_state_combo] = function
                #print(f'Function {node_state_combo} before BCF: ', function)
                #print(f'Function {node_state_combo} after BCF: ', BCF, '\n')

    return functions

