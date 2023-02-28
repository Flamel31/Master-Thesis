import sys
import os
import numpy as np

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # Read file path
        read_file_path = sys.argv[1]
        # Write file path
        dataset_path, dataset_file = os.path.split(read_file_path)
        write_file_path = os.path.join(dataset_path,"w_"+dataset_file)
        if len(sys.argv) >= 3:
            write_file_path = sys.argv[2]
        with open(read_file_path,"r") as fr:
            # Banner (first line)
            banner = fr.readline()
            if "pattern" in banner:
                with open(write_file_path,"w") as fw:
                    fw.writelines(banner.replace("pattern","real"))
                    # Header is the first line that is not a comment after the banner
                    header = False
                    # For each line
                    for line in fr:
                        # If the line is not a comment
                        if line[0] != "%":
                            if header:
                                w = 63*np.random.rand()+1
                                fw.writelines(line[:-1] + " %.2f\n"%w)
                            else:
                                fw.writelines(line)
                                header = True
    else:
        print("Correct usage: python add_random_weight.py input_dataset [output_dataset]")
    