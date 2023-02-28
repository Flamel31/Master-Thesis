import sys
import os
from zipfile import ZipFile

if len(sys.argv) >= 2:
    # Zip File
    zip_full_path = sys.argv[1]
    # Zip Path
    zip_folder_path, zip_file_name = os.path.split(zip_full_path)
    with ZipFile(zip_full_path, "r") as zip_file:
        folder = os.path.splitext(zip_file_name)[0]
        if len(sys.argv) >= 3:
            folder = sys.argv[2]
        # Temp directory
        temp_path = os.path.join(zip_folder_path,folder)
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        # Extract directory
        zip_file.extractall(temp_path)  
else:
    print("Correct usage: python unzip.py zip_path [unzip_folder]")