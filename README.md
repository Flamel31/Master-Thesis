# Parallel solvers for shortest paths and distance fields on graphs
Repository for the code used during the testing for the Master Thesis on "[Parallel solvers for shortest paths and distance fields on graphs](https://github.com/Flamel31/Master-Thesis/blob/645a353f0188093e773eab1eb6a6c54ca0c47da0/NicholasGazzo4498892_Thesis.pdf)". 

## Thesis abstract
<p align="justify">
Finding the shortest path and/or distances from single source vertex to all the vertices in a graph is a common problem in graph analytics. The Dijkstra’s
algorithm, a known reference approach for these problems, offers the most efficient computation complexity, however it doesn’t expose any kind of parallelism across
vertices. The Bellman-Ford algorithm instead, despite a more redundant work, offers a high degree of parallelism, which can be exploited by modern GPU architectures to
improve the performances on large graph structures.
</p>
<p align="justify">
This thesis presents a comparison, at the state-of-art, between the available GPU graph analytics libraries, and their parallel implementation of the Bellman-Ford algorithm,
over the sequential algorithms that runs on the CPU. Our experiments focus on monitoring how the speedup of the parallel algorithm is affected by changes in the graph metrics (e.g., a higher average degree/graph density) for specific groups of graph datasets, such as: random generated graphs and mesh graphs. The experimental results show that, except for particular cases, the most notable speedup values are always obtained on larger graph structures.
</p>

## How to compile the experiments
Copy the content of the gunrock folder in this repository inside the gunrock folder provided by the [Gunrock repository](https://github.com/gunrock/gunrock).
Then follow the [Quick start guide](https://github.com/gunrock/gunrock#quick-start-guide) to compile the library.

Nicholas Gazzo, 4498892
