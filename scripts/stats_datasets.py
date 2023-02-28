import sys
import os
import pandas as pd
import numpy as np

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        f = open(sys.argv[1],"r")
        stats = {
            "Dataset Class":[],
            "Dataset":[],
            "Vertices":[],
            "Edges":[],
            "Density":[],
            "Maximum degree":[],
            "Minimum degree":[],
            "Average degree":[],
            "Average degree variance":[],
            "Global clustering coefficient":[],
            "Average clustering coefficient":[],
            "Dijkstra Avg Time":[],
            "SLF-LLL Avg Time":[],
            "Gunrock Avg Time":[],
            "Speedup SLF-LLL over Dijkstra":[],
            "Speedup Gunrock over Dijkstra":[],
            "Speedup Gunrock over SLF-LLL":[],
            "Average visited Dijkstra":[],
            "Average visited SLF-LLL":[],
            "Average visited Gunrock":[]    
        }

        types = {
            "Vertices":np.uintc,
            "Edges":np.uintc,
            "Maximum degree":np.uintc,
            "Minimum degree":np.uintc
        }
        for line in f.readlines():
            # Building path to files
            dataset_full_path = line.rstrip('\n')
            dataset_path, dataset_file = os.path.split(dataset_full_path)
            dataset_name, dataset_ext = os.path.splitext(dataset_file)
            dataset_folder = os.path.split(dataset_path)[1]
            times_path = os.path.join(dataset_path,"csv")
            times_csv = os.path.join(times_path,dataset_name+"_times.csv")
            visited_csv = os.path.join(times_path,dataset_name+"_visited.csv")
            frontier_csv = os.path.join(times_path,dataset_name+"_frontier.csv")
            info_path = os.path.join(dataset_path,"info")
            info_csv = os.path.join(info_path,dataset_name+"_info.csv")
            # Reading the csv file
            if os.path.exists(times_csv) and os.path.exists(info_csv):
                # Read Banner
                graph_info = pd.read_csv(info_csv).loc[0]
                # Append Name
                stats["Dataset Class"].append(dataset_folder)
                stats["Dataset"].append(dataset_name)
                # Vertices and Edges
                stats["Vertices"].append(graph_info["Vertices"])
                stats["Edges"].append(graph_info["Edges"])
                # Density
                stats["Density"].append(graph_info["Density"])
                # Degrees Metrocs
                stats["Maximum degree"].append(graph_info["Maximum degree"])
                stats["Minimum degree"].append(graph_info["Minimum degree"])
                stats["Average degree"].append(graph_info["Average degree"])
                stats["Average degree variance"].append(graph_info["Average degreee variance"])
                # Clustering Coefficients
                stats["Global clustering coefficient"].append(graph_info["Global clustering coefficient"])
                stats["Average clustering coefficient"].append(graph_info["Average clustering coefficient"])
                # Append Times and Speedup
                graph_times = pd.read_csv(times_csv)
                dij = np.average(graph_times["Dijkstra"])
                slf = np.average(graph_times["SLF-LLL"])
                gun = np.average(graph_times["Gunrock"])
                stats["Dijkstra Avg Time"].append(dij)
                stats["SLF-LLL Avg Time"].append(slf)
                stats["Gunrock Avg Time"].append(gun)
                stats["Speedup SLF-LLL over Dijkstra"].append(dij/slf)
                stats["Speedup Gunrock over Dijkstra"].append(dij/gun)
                stats["Speedup Gunrock over SLF-LLL"].append(slf/gun)
                if os.path.exists(visited_csv):
                    graph_visited = pd.read_csv(visited_csv)                    
                    stats["Average visited Dijkstra"].append(np.average(graph_visited["Dijkstra"]))
                    stats["Average visited SLF-LLL"].append(np.average(graph_visited["SLF-LLL"]))
                if os.path.exists(frontier_csv):
                    graph_frontier = pd.read_csv(frontier_csv)
                    frontier_size = graph_frontier.groupby("Execution")["Frontier Size"].sum().mean()
                    stats["Average visited Gunrock"].append(frontier_size)
        stats = pd.DataFrame(stats).astype(types)
        stats.to_csv(sys.argv[2],index=False)
        f.close()
    else:
        print("Correct usage: python stats_datasets.py dataset_list output_file")
    