import cudf
import cugraph
import sys


if len(sys.argv) >= 2:
    # Read .mtx file and store it on GPU DataFrame
    df = cudf.read_csv(sys.argv[1], delimiter=" ",
        names=["source","destination","weight"],
        dtype=["int32","int32","float32"], 
        header=None, comment="%")
    # Remove first line which doesn't contain edge informations
    df = df[1:]
    
    # Building Graph
    
    edge_attr = "weight"
    if df["weight"].isna().any():
        edge_attr = None
        
    G = cugraph.from_cudf_edgelist(df,edge_attr=edge_attr, renumber=True)
    print("Graph: ",sys.argv[1])
    print("Vertices: ",G.number_of_vertices())
    print("Edges: ",G.number_of_edges())
    
    # BFS Traversal
    source_node = G.nodes().loc[0]
    if len(sys.argv) >= 3:
        source_node = int(sys.argv[2])
    distances = cugraph.bfs(G,source_node)
    unreachable = distances[distances["predecessor"]==-1]
    unreachable = unreachable[unreachable["distance"]!=0]
    if unreachable.shape[0] > 0:
        print("The graph is not totally connected, there are ",unreachable.shape[0]," unreachable vertices starting from ",source_node,".")
        print(unreachable)
    else:
        print("The graph is totally connected, all vertices are reachable starting from ",source_node,".")
