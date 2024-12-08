# petriEBN
Representing expanded boolean networks as Petri nets to compute Morse Graphs of ODE models.

## install and setup
Ensure you have a working install of python (version 3.6 or later).
Then, from the root of this repository, run `pip install .`.

## example
See `/example.py` for an example of how to use the package to compute 
characteristics of the network.

## references

This code accompanies the paper
`E. Andreas, E. Quist, and T. Gedeon. Petri Net on Expanded Boolean Network Computes Morse 
Graphs of ODE Models. (In Progress)` 

This code relies on an (adapted) implementation of the Quine-McCluskey algorithm provided by 
`X. Gan and R. Albert. General method to find the attractors of discrete dynamic models of
biological systems. PHYSICAL REVIEW E, 97:042308, 2018.`
which can be found on GitHub: `https://github.com/jackxiaogan/Multi-level_motif_algorithm`
