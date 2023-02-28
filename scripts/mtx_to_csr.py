import sys
import os
import pandas as pd
import numpy as np

gunrock_command = "./gunrock/build/bin/csr_binary %s %s"

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        f = open(sys.argv[1],"r")
        for line in f.readlines():
            # Building path to files
            dataset_full_path = line.rstrip('\n')
            dataset_path, dataset_file = os.path.split(dataset_full_path)
            dataset_name, dataset_ext = os.path.splitext(dataset_file)
            dataset_full_path_csr = os.path.join(dataset_path,dataset_name+".csr")
            if not os.path.exists(dataset_full_path_csr): 
                # Taking time for the dataset
                print("Converting %s" % dataset_name)
                os.system(gunrock_command % (dataset_full_path,dataset_full_path_csr))
                os.remove(dataset_full_path)
        f.close()
    else:
        print("Correct usage: python mtx_to_csr.py dataset_list")
    