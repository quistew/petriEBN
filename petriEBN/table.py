import itertools

import DSGRN
import petriEBN.dsgrn_support as Support

def get_input_vals(poly):
    toReturn = ""
    while True:
        idx = poly.find("[")
        if idx == -1:
            break
        toReturn += poly[idx-1]
        poly = poly[idx+1:]
    return toReturn

def get_row_input(input_string):
    var_mapping = get_input_vals(input_string)
    
    identifier = input_string.split('=')[0].strip()
    
    # will return something like this:
    # {
    #   "identifier": "p0",
    #   "input_vals": "['L', 'U']" (implied for an ordering X1, X2, ...)
    # }
    return {"identifier": identifier, "input_vals": var_mapping.__str__()}

def get_row_output(partial_order_str, identifier):
    ident_idx = partial_order_str.find(identifier)
    search_string = partial_order_str[:ident_idx]
    return search_string.count('T')

def get_partial_order_dict(partial_orders_str):
    d = {}
    pos = partial_orders_str.split("\n")
    for item in pos:
        mp = item.split(':')
        assert(len(mp) == 2)
        d[mp[0].strip()] = mp[1].strip()
    
    return d

def obtain_network_nodes(network_string):
    net_nodes = []
    for l in network_string.split('\n'):
        m = l.find(' : ')
        net_nodes.append(l[:m])
    return net_nodes

def obtain_network_edges(network_string):
    net_nodes = obtain_network_nodes(network_string)
    edge_dict = {}
    for n in net_nodes:
        edge_dict[n] = []
    network_string_list = network_string.split('\n')

    for l in network_string_list:
        for n2 in net_nodes:
            if n2+' :' in l:
                for n1 in net_nodes:
                    l2 = l[l.find(':'):]
                    neg = 0
                    if n1 in l2:
                        if '~' == l2[l2.find(n1)-1:l2.find(n1)]:
                            neg = 1
                        edge_dict[n2].append((n1,neg))
    for n in net_nodes:
        if edge_dict[n] == []:
            del edge_dict[n]
    return edge_dict
###


def obtain_network_states(network_string):
    nodes = obtain_network_nodes(network_string)
    node_states = {}
    for n in nodes:
        if network_string.count(n) >1:
            node_states[n] = list(range(network_string.count(n)))
        else:
            node_states[n] = list(range(network_string.count(n)+1))
    return node_states


def get_table(network_string, pgi):
    fullnodelist = sorted(obtain_network_nodes(network_string))
    edge_dict = obtain_network_edges(network_string)
    
    network = DSGRN.Network(network_string)
    pg = DSGRN.ParameterGraph(network)
    param = pg.parameter(pgi)

    get_partial_order_str = Support.get_partial_order(network_string, fullnodelist, param)
    partial_orders = get_partial_order_dict(get_partial_order_str)

    functions = {}
    for n2 in fullnodelist: 
        functions[n2] = {}
        node = network.index(n2)
        for poly in DSGRN.parameter_input_polynomials(param, node).split('\n'):
            word = ''
            for n1,rep in sorted(edge_dict[n2]):
                input = poly[poly.find(n1+'->')-2:poly.find(n1+'->')-1]
                word += input
            poly_name = poly[:poly.find(' = ')]
            #print(partial_orders[n2])
            #print(partial_orders[n2][:partial_orders[n2].find(poly_name)])
            if partial_orders[n2].find(poly_name+',') != -1:
                output = partial_orders[n2][:partial_orders[n2].find(poly_name+',')].count('T')
            else:
                output = partial_orders[n2][:partial_orders[n2].find(poly_name+')')].count('T')
            functions[n2][word] = output
            #print(poly_name,word,output)
    return functions 



### table conversion functions ###

def obtain_network_thresholds(edge_dict):
    thresholds = {}
    for n2 in edge_dict:
        for n1,neg in edge_dict[n2]:
            t = f'T[{n1}->{n2}]'
            if n1 not in thresholds:
                thresholds[n1] = [t]
            else:
                thresholds[n1].append(t)
    return thresholds

def obtain_threshold_ordering(pgi, edge_dict, parametergraph):
    thresholds = obtain_network_thresholds(edge_dict)
    param = parametergraph.parameter(pgi)
    po_list = param.partialorders('T').split('\n')
    threshold_order = {}
    for po in po_list:
        n = po[:po.find(' :')] 
        if n in thresholds:
            t_order = [t[0] for t in sorted([(t,po.find(t)) for t in thresholds[n]],key=lambda x: x[1])]
        else:
            t_order = ['t0']
        threshold_order[n] = t_order
    return threshold_order

def obtain_LU_state_values(edge_dict, threshold_order):
    LU_decop = {}
    for n2 in edge_dict:
        for n1,neg in edge_dict[n2]:
            #if n1 in edge_dict:
                LU_decop[(n1,n2)] = {}
                t = f'T[{n1}->{n2}]'
                if n1 in threshold_order:
                    t_index = threshold_order[n1].index(t)
                    upper_bound = len(threshold_order[n1])
                else:
                    t_index = 0
                    upper_bound = 1
                LU_decop[(n1,n2)]['L'] = list(range(t_index+1))
                LU_decop[(n1,n2)]['U'] = list(range(t_index+1,upper_bound+1))

    return LU_decop   

def obtain_param_as_table(network_string, pgi):
    fullnodelist = sorted(obtain_network_nodes(network_string))
    #print(fullnodelist)
    edge_dict = obtain_network_edges(network_string)
    #print(edge_dict)
    parametergraph = DSGRN.ParameterGraph(DSGRN.Network(network_string))
    LU = get_table(network_string, pgi)
    #print(LU)
    threshold_order = obtain_threshold_ordering(pgi, edge_dict, parametergraph)
    #print('threshold order: ', threshold_order)
    LU_decomp = obtain_LU_state_values(edge_dict, threshold_order)
    #print('LU decomp: ',LU_decomp)
    params_as_input_outputs = {}
    for n2 in fullnodelist:
        if n2 in edge_dict:
            all_input = []
            for word in LU[n2]:
                output = LU[n2][word]
                specific_input = []
                for n1,neg in sorted(edge_dict[n2]):
                    input = word[edge_dict[n2].index((n1, neg))]
                    if neg == 1: # accounting for repressing edge
                        if input == 'L':
                            input = 'U'
                        else:
                            input = 'L'
                    specific_input.append(LU_decomp[(n1,n2)][input])
                specific_input.append([output])
                all_input += [list(i) for i in itertools.product(*specific_input)]
            params_as_input_outputs[n2] = all_input
    return params_as_input_outputs

# TODO :: there is an error in our code, the LU decomp is in the order of 
# the input poly and not the order of the nodelist.


