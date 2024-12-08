import petriEBN.table as Table
from petriEBN.extended_graph import ExtendedGraph
from petriEBN.extended_graph import obtain_BCF_functions, obtain_EG_edges
from petriEBN.phi import NodeConfigurations, ChainSupport, CycleAnalysis

# initialize the network string and parameters (see https://dsgrn.readthedocs.io/en/latest/)
network_string = 'X1 : (X2)\nX2 : (~X1)(~X3)\nX3 : (X1+X3)' # the string defining the network
nodelist = ['X1', 'X2', 'X3'] # the list of nodes in the network
pgi = 259 # the parameter graph index to use

# obtain network states and functions for the expanded graph
node_states = Table.obtain_network_states(network_string)
functions = obtain_BCF_functions(network_string, pgi, node_states)
EG_edges = obtain_EG_edges(node_states, functions)

# create an ExtendedGraph instance and get virtual and composite nodes
extended_graph = ExtendedGraph(EG_edges)
in_V_s, in_V_c = extended_graph.get_virtual_and_composite_nodes()

# get all C0 configurations
node_configurations = NodeConfigurations(in_V_c, nodelist)
all_C0 = node_configurations.find_all_C0()

# find support chains based on the C0 configurations
chain_support = ChainSupport(in_V_s, in_V_c)
support_chains = chain_support.find_support_chains(all_C0)

# analyze cycles and fixed points from support chains
cycle_analysis = CycleAnalysis(support_chains, nodelist)
cycles, fixed_points = cycle_analysis.get_cycles_and_fixed_points()

# classify cycles as full or partial
full_cycles, partial_cycles = cycle_analysis.categorize_cycles(cycles)

# output results
print("Cycles:", cycles)
print("Fixed Points:", fixed_points)
print("Full Cycles:", full_cycles)
print("Partial Cycles:", partial_cycles)