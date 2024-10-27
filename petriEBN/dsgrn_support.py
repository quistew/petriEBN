import DSGRN

'''Support Functions for DSGRN'''

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
    return edge_dict

def get_partial_order_for_node_with_no_out_edges(network_string, node, p):
    '''DSGRN v 1.5.0 doesn't give a partial ordering of dummy threshold for a node 
    with no out edge, this function finds that partial ordering. Use to determine when
    a node is activated by its inputs.'''


    all_input_poly = [(i.split(' = ')[0], i.split(' = ')[-1]) for i in DSGRN.parameter_input_polynomials(p, DSGRN.Network(network_string).index(node)).split('\n')]
    below_t = '('
    above_t = 'T['+node+'->], '
    dummy_threshold = f'T[{node}->]'
    inequalities = p.inequalities().split('"')[3]
    for i in inequalities.split('&&'):
        if node+'->' in i:
            for name,polynomial in all_input_poly:
                if polynomial in i:
                    if '< '+dummy_threshold in i:
                        below_t += name+', '
                    else:
                        above_t += name+', '

    po = below_t+above_t[:-2]+')'
    return po

def get_partial_order(network_string, fullnodelist, param):
    network = DSGRN.Network(network_string)
    need_DSGRN_support_function = False
    for n in fullnodelist:
        if network.outputs(network.index(n)) == []:
            need_DSGRN_support_function = True

    if need_DSGRN_support_function == False:
        partial_orders_str = param.partialorders('T')
    else:
        partial_orders_str = ''
        po = param.partialorders('T').split('\n')
        for p in po:
            if '(p0, p1)' in p:
                node = p[:p.find(' : ')]
                p_updated = get_partial_order_for_node_with_no_out_edges(network_string, node, param)
                partial_orders_str = node + ' : ' +partial_orders_str+p_updated+'\n'
            else:
                partial_orders_str = partial_orders_str+p+'\n'
        partial_orders_str = partial_orders_str[:-2]

    return partial_orders_str

def get_index_from_partial_order_when_network_has_node_wo_outedges(network_string, po):
    '''DSGRN v 1.5.0 `index_from_partial_orders` has a bug when a network has a node with no out edges.
    This function determines the parameter index from a partial order in this case. Not efficient, use
    only when necessary.'''

    parametergraph = DSGRN.ParameterGraph(DSGRN.Network(network_string))
    issue_nodes = []
    po_string = []
    for o1 in po:
        if len(o1) == 2:
            issue_nodes.append(DSGRN.Network(network_string).name(po.index(o1)))
        o2 = '('+', '.join(o1)+')'
        po_string.append(o2)

    for p in range(parametergraph.size()):
        parameter = parametergraph.parameter(p)
        good = True
        for node in issue_nodes:
            if get_partial_order_for_node_with_no_out_edges(network_string, node, parameter) != '(p0, t0, p1)':
                good = False

        if good == True:
            part_orders = parameter.partialorders().split('\n')
            partial_orders = [p_order.split(':')[1].strip() for p_order in part_orders if p_order.split(':')[1].strip() == po_string[part_orders.index(p_order)]]
    
            if len(partial_orders) == len(po_string):
                print(p)
                return p
            elif p == parametergraph.size()-1:
                return -1
 
def non_essential_edges(network_string,pgi):
    parametergraph = DSGRN.ParameterGraph(DSGRN.Network(network_string))
    param = parametergraph.parameter(pgi)
    po = param.partialorders().split('\n')
    ne_edges = []
    for word in po:
        node = word.split(' : ')[0]
        polynomial = word.split(' : ')[1]
        if 't' not in polynomial:
            polynomial = get_partial_order_for_node_with_no_out_edges(network_string, node, pgi)
        split_polynomial = polynomial[1:-1].split(', ')
        index = DSGRN.Network(network_string).index(node)

        poly_dict = {}
        for poly in DSGRN.parameter_input_polynomials(param, index).split('\n'):
            poly_dict[poly.split(' = ')[0]] = poly.split(' = ')[1]

        inputs = [DSGRN.Network(network_string).name(n) for n in DSGRN.Network(network_string).inputs(index)]
 
        for input in inputs:
            between = {}
            above = 0
            expression = f'[{input}->{node}]'
            for express in range(len(split_polynomial)):
                if 'p' in split_polynomial[express]:
                    input_value = poly_dict[split_polynomial[express]][poly_dict[split_polynomial[express]].find(expression)-1]
                    if above not in between:
                        between[above] = [input_value]
                    else:
                        between[above].append(input_value)
                else:
                    above +=1
            essential = False
            for i in between:
                if len(set(between[i])) == 1:
                    essential = True
            if essential == False:
                ne_edges.append((input, node))

    return ne_edges

def get_morse_graph_annotation(network_string, pgi = None):
    network = DSGRN.Network(network_string)
    pg = DSGRN.ParameterGraph(network)
    if pgi == None:
        for par_index in range(0,pg.size()):
            morsegraph = DSGRN.MorseGraph(DSGRN.DomainGraph(pg.parameter(par_index)))
            MG = [morsegraph.annotation(i)[0] for i in range(0, morsegraph.poset().size())]
            MG_stable = [morsegraph.annotation(i)[0] for i in range(0, morsegraph.poset().size()) if len(morsegraph.poset().children(i)) == 0]
            print(par_index, 'All: ', MG, 'Stable: ', MG_stable)
    else:
        morsegraph = DSGRN.MorseGraph(DSGRN.DomainGraph(pg.parameter(pgi)))
        MG = [morsegraph.annotation(i)[0] for i in range(0, morsegraph.poset().size())]
        MG_stable = [morsegraph.annotation(i)[0] for i in range(0, morsegraph.poset().size()) if len(morsegraph.poset().children(i)) == 0]
        print(pgi, 'All: ', MG, 'Stable: ', MG_stable)

        return (MG, MG_stable)