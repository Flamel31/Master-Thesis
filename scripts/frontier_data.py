import sys
import os
import pandas as pd
import numpy as np

gunrock_command_1 = "./gunrock/build/bin/sssp_frontier %s %d >> %s"
gunrock_command_2 = "./gunrock/build/bin/sssp_visited %s %d >> %s"

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        rep = int(sys.argv[2])
        f = open(sys.argv[1],"r")
        for line in f.readlines():
            # Building path to files
            dataset_full_path = line.rstrip('\n')
            dataset_path, dataset_file = os.path.split(dataset_full_path)
            dataset_name, dataset_ext = os.path.splitext(dataset_file)
            csv_path = os.path.join(dataset_path,"csv")
            if not os.path.exists(csv_path):
                os.mkdir(csv_path)
            dataset_csv_1 = os.path.join(csv_path,dataset_name+"_frontier.csv")
            if os.path.exists(dataset_csv_1): 
                os.remove(dataset_csv_1)
                print("Taking frontiers data for %s" % dataset_name)
                os.system(gunrock_command_1 % (dataset_full_path,rep,dataset_csv_1))
                # Fixing iteration count and adding a column for the execution
                df = pd.read_csv(dataset_csv_1)
                # Iteration from 1 to n
                df["Iteration"] += 1
                # Set execution index
                executions = np.zeros(df.shape[0],dtype="int")
                indices = np.where(df["Iteration"] == 1)[0]
                for i in range(1,len(indices)):
                    executions[indices[i-1]:indices[i]] = i
                executions[indices[-1]:] = len(indices)
                df["Execution"] = executions
                df.to_csv(dataset_csv_1,index=False)
            dataset_csv_2 = os.path.join(csv_path,dataset_name+"_visited.csv")
            if not os.path.exists(dataset_csv_2): 
                # os.remove(dataset_csv_2)
                print("Taking visited neigh cpu for %s" % dataset_name)
                os.system(gunrock_command_2 % (dataset_full_path,rep,dataset_csv_2))
            dataset_csv_3 = os.path.join(csv_path,dataset_name+"_frontier_time.csv")
            if os.path.exists(dataset_csv_3): 
                 os.remove(dataset_csv_3)
        f.close()
    else:
        print("Correct usage: python frontier_data.py dataset_list num_repetition")
    