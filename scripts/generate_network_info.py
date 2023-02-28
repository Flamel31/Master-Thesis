import sys
import os
import pandas as pd
import numpy as np

command = "./gunrock/build/bin/network_info %s >> %s"

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        f = open(sys.argv[1],"r")
        for line in f.readlines():
            # Building path to files
            dataset_full_path = line.rstrip('\n')
            dataset_path, dataset_file = os.path.split(dataset_full_path)
            dataset_name, dataset_ext = os.path.splitext(dataset_file)
            dataset_folder = os.path.split(dataset_path)[1]
            info_path = os.path.join(dataset_path,"info")
            if not os.path.exists(info_path):
                os.mkdir(info_path)
            dataset_info_csv = os.path.join(info_path,dataset_name+"_info.csv")
            if not os.path.exists(dataset_info_csv):
                print("Generating network info for %s"%dataset_full_path)
                os.system(command%(dataset_full_path,dataset_info_csv))
        f.close()
    else:
        print("Correct usage: python generate_network_info.py dataset_list")
    