import sys
import os
import pandas as pd
import numpy as np

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        frontier_df = {"Dataset":[],"Frontier Size":[],"Elapsed Time":[],"Iteration":[]}
        with open(sys.argv[1],"r") as in_f:
            for line in in_f.readlines():
                # Building path to files
                dataset_full_path = line.rstrip('\n')
                dataset_path, dataset_file = os.path.split(dataset_full_path)
                dataset_name, dataset_ext = os.path.splitext(dataset_file)
                csv_path = os.path.join(dataset_path,"csv")
                dataset_csv = os.path.join(csv_path,dataset_name+"_frontier.csv")
                if os.path.exists(dataset_csv): 
                    df = pd.read_csv(dataset_csv)
                    df = df[df["Frontier Size"] > 0]
                    mean_iteration = int(df.groupby("Execution")["Iteration"].max().mean())
                    mean_frontiers = df.groupby("Iteration").mean()[:mean_iteration]
                    for i in range(mean_frontiers.shape[0]):
                        frontier_df["Dataset"].append(dataset_name)
                    for i in mean_frontiers["Frontier Size"].tolist():
                        frontier_df["Frontier Size"].append(i)
                    for i in mean_frontiers["Elapsed Time"].tolist():
                        frontier_df["Elapsed Time"].append(i)
                    for i in mean_frontiers.index.tolist():
                        frontier_df["Iteration"].append(i)
            frontier_df = pd.DataFrame(frontier_df)
            frontier_df.to_csv(sys.argv[2],index=False)
    else:
        print("Correct usage: python frontier_stats.py dataset_list output_file")
    