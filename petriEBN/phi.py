import itertools as it
from collections import Counter

import DSGRN

from petriEBN.expanded_graph import BOOL_AND, ExpandedGraph

class NodeConfigurations:
    def __init__(self, composite_nodes, nodelist):
        """
        Initialize with composite nodes and a list of all nodes in the network.
        
        Args:
            composite_nodes (dict): Composite nodes and the virtual nodes they support.
            nodelist (list): List of all nodes in the network.
        """
        self.composite_nodes = composite_nodes
        self.nodelist = nodelist
    
    def find_all_C0(self):
        """Find all C0 configurations satisfying certain conditions."""
        all_C0 = []
        combinations = [list(combo) for k in range(2, len(self.composite_nodes) + 1)
                        for combo in it.combinations(self.composite_nodes.keys(), k)]

        for combo in combinations:
            virtual_nodes = {v for node in combo for v in node.split(f' {BOOL_AND} ')}
            
            if len(virtual_nodes) > len(self.nodelist):
                continue
            
            sisters = [v.split('$')[0] for v in virtual_nodes]
            if not any(count > 1 for count in Counter(sisters).values()):
                all_C0.append(combo)
        
        return all_C0


class ChainSupport:
    def __init__(self, virtual_nodes, composite_nodes):
        """
        Initialize with virtual and composite nodes.
        
        Args:
            virtual_nodes (dict): Virtual nodes and their supporting composite nodes.
            composite_nodes (dict): Composite nodes and the virtual nodes they support.
        """
        self.virtual_nodes = virtual_nodes
        self.composite_nodes = composite_nodes
    
    def find_support_chains(self, all_C0):
        """Identify support chains that include completely focal sets."""
        support_chains = []
        
        for c0 in all_C0:
            s = sorted({j for node in c0 for j in self.composite_nodes[node]})
            main_composites = list({j for v in s for j in self.virtual_nodes[v]})

            for subset in it.chain.from_iterable(it.combinations(main_composites, k) for k in range(1, len(main_composites) + 1)):
                if all(set(s).intersection(self.virtual_nodes.get(v, [])) for v in subset):
                    chain = [sorted(list(subset)), sorted(list(s)), sorted(list(c0))]
                    if chain not in support_chains:
                        support_chains.append(chain)
        
        return support_chains


class CycleAnalysis:
    def __init__(self, support_chains, nodelist):
        """
        Initialize with support chains and a list of all nodes in the network.
        
        Args:
            support_chains (list): List of support chains.
            nodelist (list): List of all nodes in the network.
        """
        self.support_chains = support_chains
        self.nodelist = nodelist

    def get_cycles_and_fixed_points(self):
        """Identify cycles and fixed points from support chains."""
        cycles, fixed_points = [], []

        for c1t, st, c2t in self.support_chains:
            if set(c1t).intersection(c2t) == set(c1t):
                fixed_points.append(st)
            else:
                cycles += self._find_cycles([[[c1t, st, c2t]]])
        
        return self._remove_permutations(cycles), fixed_points

    def _find_cycles(self, todo):
        """Recursive helper to find cycles."""
        cycles = []
        while todo:
            chain = todo.pop()
            c1t, st, c2t = chain[0]

            for c1s, ss, c2s in self.support_chains:
                if c1t == c2s and [c1s, ss, c2s] not in chain:
                    todo.append([[c1s, ss, c2s], *chain])
                    if [c1s, ss, c2s] == chain[-1]:
                        cycles.append(chain)

        return cycles

    def _remove_permutations(self, cycles):
        """Filter out permutations of cycles."""
        unique_cycles = []
        seen = []

        for cycle in cycles:
            ordered_cycle = sorted(set(cycle))
            if ordered_cycle not in seen:
                unique_cycles.append(cycle)
                seen.append(ordered_cycle)

        return unique_cycles

    def categorize_cycles(self, cycles):
        """Categorize cycles as full or partial based on node changes."""
        full_cycles, partial_cycles = [], []
        
        for cycle in cycles:
            changed = [False] * len(self.nodelist)
            c1s, ss, _ = cycle[0]
            
            for _, s, _ in cycle[1:]:
                for i, state in enumerate(s):
                    if state != ss[i]:
                        changed[i] = True
            
            if all(changed):
                full_cycles.append(cycle)
            elif sum(changed) > 1:
                partial_cycles.append(cycle)
        
        return full_cycles, partial_cycles


class MorseGraphAnnotator:
    def __init__(self, network_string):
        """Initialize the annotator with a network string."""
        self.network = DSGRN.Network(network_string)
        self.parameter_graph = DSGRN.ParameterGraph(self.network)
    
    def annotate_morse_graph(self, parameter_index=None):
        """Annotate the Morse graph for a specific or all parameters."""
        if parameter_index is None:
            for index in range(self.parameter_graph.size()):
                self._print_annotations(index)
        else:
            self._print_annotations(parameter_index)
    
    def _print_annotations(self, parameter_index):
        morse_graph = DSGRN.MorseGraph(DSGRN.DomainGraph(self.parameter_graph.parameter(parameter_index)))
        annotations = [morse_graph.annotation(i)[0] for i in range(morse_graph.poset().size())]
        stable_annotations = [annotations[i] for i in range(morse_graph.poset().size()) if not morse_graph.poset().children(i)]
        print(parameter_index, 'All:', annotations, 'Stable:', stable_annotations)
