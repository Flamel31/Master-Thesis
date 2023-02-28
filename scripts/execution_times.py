import sys
import os
import pandas as pd
import numpy as np

gunrock_command = "./gunrock/build/bin/sssp_compare %s %d >> %s"

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        rep = int(sys.argv[2])
        algorithms = 3
        f = open(sys.argv[1],"r")
        for line in f.readlines():
            # Building path to files
            dataset_full_path = line.rstrip('\n')
            dataset_path, dataset_file = os.path.split(dataset_full_path)
            dataset_name, dataset_ext = os.path.splitext(dataset_file)
            csv_path = os.path.join(dataset_path,"csv")
            if not os.path.exists(csv_path):
                os.mkdir(csv_path)
            dataset_csv = os.path.join(csv_path,dataset_name+"_times.csv")
            if os.path.exists(dataset_csv): 
                os.remove(dataset_csv)
            # Taking time for the dataset
            print("Taking times for %s" % dataset_name)
            os.system(gunrock_command % (dataset_full_path,rep,dataset_csv))
        f.close()
    else:
        print("Correct usage: python execution_times.py dataset_list num_repetition")
    