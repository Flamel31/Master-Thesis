import sys
import os
from zipfile import ZipFile

datasets_path = "./datasets/"

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # Url to get the dataset
        url = sys.argv[1]
        # Zip file name
        zip_name = os.path.split(url)[1]
        # Dataset name
        dataset_name = os.path.splitext(zip_name)[0]
        # Path where to store the dataset
        dataset_folder = os.path.join(datasets_path,dataset_name)
        if not os.path.exists(dataset_folder):
            os.mkdir(dataset_folder)
        # Path of the zip file
        zip_path = os.path.join(dataset_folder,zip_name)
        # Download the zip file
        os.system("wget %s -P %s"%(url,dataset_folder))
        with ZipFile(zip_path, "r") as zip_file:
            # Temp directory
            temp_path = os.path.join(dataset_folder,"temp")
            os.mkdir(temp_path)
            # Extract directory
            zip_file.extractall(temp_path)  
    else:
        print("Correct usage: python download_dataset.py dataset_url ")