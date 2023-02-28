import numpy as np
import sys
import os

folder_path = "./datasets/random/random%d"
file_name = "rand%d_%s.%s"

def generate_mtx(vertices,prob,path):
    print("Generating mtx network for prob %f"%prob)
    # Generating adjacency matrix
    adj_matrix = np.random.random_sample((vertices,vertices))
    mask = adj_matrix<prob_list[j]
    np.fill_diagonal(mask,False)
    edges = np.sum(mask)
    # Generating weight [1,64)
    weights = 63*np.random.random_sample(edges)+1
    source, dest = np.where(mask)
    with open(random_path,"w") as f:         
        f.writelines(["%%MatrixMarket matrix coordinate real general\n",
            "%d %d %d\n"%(vertices,vertices,edges)])
        for i in range(edges):
            f.writelines("%d %d %.2f\n"%(source[i]+1,dest[i]+1,weights[i]))

def generate_csr(vertices,prob,path):
    print("Generating csr network for prob %f"%prob)
    os.system("./gunrock/build/bin/random_network %d %f %s"%(vertices,prob,path))

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        # Format Mtx or Csr (Binary)
        output_format = sys.argv[1].lower()
        if output_format in ["mtx","csr"]:
            # Number of vertices
            vertices = int(sys.argv[2])
            # How Many Graph to generate
            generate_number = 8
            if len(sys.argv) >= 4:
                generate_number = int(sys.argv[3])
            if not os.path.exists(folder_path%vertices):
                os.mkdir(folder_path%vertices)
            # Probability of generating an edge between i and j
            prob_list = [1.0 / (2**i) for i in range(generate_number)]
            prob_h = ["%d"%(prob*100) if prob*100 >= 1 else ("%.2f"%(prob*100)).replace(".","") for prob in prob_list]
            for j in range(len(prob_list)):
                random_path = os.path.join(folder_path%vertices,file_name%(vertices,prob_h[j],output_format))
                if not os.path.exists(random_path):
                    if output_format == "mtx":
                        generate_mtx(vertices,prob_list[j],random_path)
                    else:
                        generate_csr(vertices,prob_list[j],random_path)
        else:
            print('Format must be "mtx" or "csr"')
    else:
        print("Correct usage: python generate_random_graph.py format(mtx/csr) num_vertices [how_many]")