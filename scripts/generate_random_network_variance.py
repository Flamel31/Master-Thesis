from functools import reduce
import numpy as np
import sys
import os

folder_path = "./datasets/random_variance/random%d"
file_name = "rand%d_%d_%d.%s"

def generate_network(vertices,mu,sigma):
    edges_per_vertex = np.ceil(np.random.normal(mu,sigma,vertices)).astype("int32")
    edges_per_vertex[edges_per_vertex < 0] = 0
    edges = int(np.sum(edges_per_vertex)) 
    if edges % 2 != 0:
        edges += 1
        edges_per_vertex[np.random.choice(range(vertices))] += 1
    # Building for csr format
    row_offsets = np.zeros(vertices+1,dtype="int32")
    for i in range(1,len(row_offsets)):
        row_offsets[i] = row_offsets[i-1] + edges_per_vertex[i-1]
    column_indices = np.full(edges,-1,dtype="int32")
    non_zero_values = 63*np.random.random_sample(edges)+1
    # For each vertex i (starting from the one with more edges)
    for i in np.flip(np.argsort(edges_per_vertex)):
        free_space = np.sum(edges_per_vertex)
        # There is no more space available
        if free_space == 0:
            break
        # How many edges are missing from vertex i
        missing_edges_i = edges_per_vertex[i]
        start_i, end_i = row_offsets[i], row_offsets[i+1]-edges_per_vertex[i]
        edges_per_vertex[i] = 0
        # Choices available for vertex i
        free_vertices = np.setdiff1d(np.where(edges_per_vertex > 0)[0],column_indices[start_i:end_i],True)
        # If the choices are not enough we need to swap some edge previously created
        while len(free_vertices) < missing_edges_i:
            # All the vertices that can be searched for a swap
            vertices_for_swap = reduce(np.setdiff1d, (range(vertices), [i], column_indices[start_i:end_i], free_vertices))
            # Searching for a vertex k1 contained in the list connected (with an edge)
            # to a vertex k2 that is also contained in the list
            for k1 in vertices_for_swap:
                start_k1, end_k1 = row_offsets[k1], row_offsets[k1+1]-edges_per_vertex[k1]
                vertices_to_swap = vertices_for_swap[np.isin(vertices_for_swap,column_indices[start_k1:end_k1])]
                # Found a matching case, swapping k1 <-> k2 with k1 <-> i and k2 <-> i
                if len(vertices_to_swap) > 0:
                    k2 = vertices_to_swap[0]
                    start_k2, end_k2 = row_offsets[k2], row_offsets[k2+1]-edges_per_vertex[k2]
                    column_indices[start_k1:end_k1][column_indices[start_k1:end_k1] == k2] = i              
                    column_indices[start_k2:end_k2][column_indices[start_k2:end_k2] == k1] = i
                    column_indices[end_i:end_i+2] = [k1,k2]
                    end_i += 2
                    missing_edges_i -= 2
                    break
        # Picking some random vertices from the available choices to fill the missing edges
        j_vertices = np.random.choice(free_vertices,size=missing_edges_i,replace=False)
        column_indices[row_offsets[j_vertices+1] - edges_per_vertex[j_vertices]] = i
        edges_per_vertex[j_vertices] -= 1
        column_indices[end_i:row_offsets[i+1]] = j_vertices
    # Sorting columns indices
    for i in range(vertices):
        column_indices[row_offsets[i]:row_offsets[i+1]] = np.sort(column_indices[row_offsets[i]:row_offsets[i+1]])
    return (row_offsets,column_indices,non_zero_values)

def generate_mtx(vertices,mu,sigma,path):
    print("Generating mtx network with %d vertices, %.2f average degree, %.2f standard deviation."%(vertices,mu,sigma))
    row_offsets,column_indices,non_zero_values = generate_network(vertices,mu,sigma)
    with open(path,"w") as out_file:
        out_file.writelines(["%%MatrixMarket matrix coordinate real symmetric\n", 
            "%d %d %d\n"%(vertices,vertices,int(len(non_zero_values)/2))])
        for i in range(vertices):
            for j in range(row_offsets[i],row_offsets[i+1]):
                if column_indices[j] < i:
                    out_file.writelines("%d %d %.2f\n"%(i+1,column_indices[j]+1,non_zero_values[j]))

            
def generate_csr(vertices,mu,sigma,path):
    print("Generating csr network with %d vertices, %f average degree, %f standard deviation."%(vertices,mu,sigma))
    row_offsets,column_indices,non_zero_values = generate_network(vertices,mu,sigma)
		
if __name__ == "__main__":
    if len(sys.argv) >= 5:
        # Format Mtx or Csr (Binary)
        output_format = sys.argv[1].lower()
        if output_format in ["mtx","csr"]:
            # Number of vertices
            vertices = int(sys.argv[2])
            # Mean
            mu = float(sys.argv[3])
            # Standard Deviation
            sigmas = np.array(sys.argv[4:]).astype("float")
            if not os.path.exists(folder_path%mu):
                os.mkdir(folder_path%mu)
            for sigma in sigmas:
                random_path = os.path.join(folder_path%mu,file_name%(vertices,mu,sigma,output_format))
                if not os.path.exists(random_path):
                    if output_format == "mtx":
                        generate_mtx(vertices,mu,sigma,random_path)
                    else:
                        generate_csr(vertices,mu,sigma,random_path)
        else:
            print('Format must be "mtx" or "csr"')
    else:
        print("Correct usage: python generate_random_graph_variance.py (mtx/csr) num_vertices mu sigma1 [sigma2] [...]")