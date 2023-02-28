import sys
import os
import numpy as np
import pandas as pd

if len(sys.argv) >= 2:
    with open(sys.argv[1],"r") as dataset_list:
        for line in dataset_list.readlines():
            # Building path to files
            dataset_full_path = line.rstrip('\n')
            print("Fixing ",dataset_full_path)
            # Read the gtaph
            graph_data = pd.read_csv(dataset_full_path,sep=' ',header=None,comment="%")
            vertices, edges = graph_data[:1].loc[0][1:]
            graph_data = graph_data[1:]
            if np.any(graph_data[[0,1]] == 0):
                graph_data[[0,1]] += 1
            # Remove edges with vertex number greater than the number of vertices
            mask = graph_data[[0,1]] <= int(vertices)
            graph_data = graph_data[np.logical_and(mask[0],mask[1])]
            edges = graph_data.shape[0]
            # Switch source, dest for source < dest
            mask = graph_data[0]<graph_data[1]
            graph_data.loc[mask,0],graph_data.loc[mask,1] = graph_data.loc[mask,1],graph_data.loc[mask,0]
            # Add random weight if necessary
            if np.isnan(np.sum(graph_data[2])):
                M.data = 63*np.random.random_sample(M.data.shape)+1
            f = open(dataset_full_path,"w")
            f.writelines(["%%MatrixMarket matrix coordinate real symmetric\n","%d %d %d\n"%(vertices,vertices,edges)])
            graph_data.to_csv(f,sep=' ',header=None,index=None)
            f.close()
else:
    print("Correct usage: python fix_dataset.py dataset_list")