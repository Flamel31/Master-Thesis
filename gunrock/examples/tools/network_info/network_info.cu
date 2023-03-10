#include <gunrock/algorithms/algorithms.hxx>
#include <gunrock/algorithms/tc.hxx>
// Reference implementations
using namespace gunrock;
using namespace memory;

void test_network_info(int num_arguments, char** argument_array) {
	if (num_arguments < 2) {
		std::cerr << "usage: ./bin/<program-name> filename.mtx" << std::endl;
		exit(1);
	}

	// Define types
	using vertex_t = int;
	using edge_t = int;
	using weight_t = float;
	using csr_t = format::csr_t<memory_space_t::device, vertex_t, edge_t, weight_t>;

	// IO
	csr_t csr;
	std::string filename = argument_array[1];
	// std::cout << filename  << std::endl;
	if (util::is_market(filename)) {
		io::matrix_market_t<vertex_t, edge_t, weight_t> mm;
		csr.from_coo(mm.load(filename));
	} else if (util::is_binary_csr(filename)) {
		csr.read_binary(filename);
	} else {
		std::cerr << "Unknown file format: " << filename << std::endl;
		exit(1);
	}

	// Build graph
	// supports row_indices and column_offsets (default = nullptr)
	auto G = graph::build::from_csr<memory_space_t::device, graph::view_t::csr>(
		csr.number_of_rows,               // rows
		csr.number_of_columns,            // columns
		csr.number_of_nonzeros,           // nonzeros
		csr.row_offsets.data().get(),     // row_offsets
		csr.column_indices.data().get(),  // column_indices
		csr.nonzero_values.data().get()   // values
	);
	
	// Vertices and Edges
	long int n_vertices = G.get_number_of_vertices();
	long int n_edges = G.get_number_of_edges();
	// Density Evaluation
	double density = (double)n_edges / (double)(n_vertices*(n_vertices-1));
	
	// Degree Metrics Evalutations
	// Copy to CPU
	thrust::host_vector<edge_t> _row_offsets(csr.row_offsets);
	edge_t* row_offsets = _row_offsets.data();
	int min_degree = std::numeric_limits<int>::max();
	int max_degree = std::numeric_limits<int>::min();
	for(vertex_t i = 0; i < n_vertices; i++){
		double degree = row_offsets[i+1] - row_offsets[i];
		if(degree < min_degree) min_degree = degree;
		if(degree > max_degree) max_degree = degree;
	}
	double avg_degree = (double)n_edges / (double)n_vertices;
	double avg_degree_variance = 0;
	for(vertex_t i = 0; i < n_vertices; i++){
		double degree = row_offsets[i+1] - row_offsets[i];
		avg_degree_variance += ((degree - avg_degree) * (degree - avg_degree));
	}
	avg_degree_variance /= n_vertices;
	// Clustering Coefficients Evaluations
	// Triangle Count
	thrust::device_vector<vertex_t> triangles_count(G.get_number_of_vertices(), 0);
	std::size_t total_triangles = 0;
	tc::run(G, true,triangles_count.data().get(), &total_triangles);
	// Copy to CPU
	thrust::host_vector<vertex_t> _triangles_count(triangles_count);
	vertex_t* triangles = _triangles_count.data();
	double C_global = 0;
	double C_avg = 0;
	for(vertex_t i = 0; i < n_vertices; i++){
		double degree = row_offsets[i+1] - row_offsets[i];
		C_global += degree * (degree - 1);
		if(degree != 0 && degree != 1)
			C_avg += (triangles[i] * 2) / (degree * (degree - 1));
	}
	C_global = (total_triangles / C_global) * 2;
	C_avg = C_avg / n_vertices;
	
	// Print
	std::cout << "Vertices,Edges,Density,Maximum degree,Minimum degree,Average degree,Average degreee variance,Global clustering coefficient,Average clustering coefficient" << std::endl;
	// Vertices and Edges
	std::cout << n_vertices << "," << n_edges << ",";
	// Density
	std::cout << density << ",";
	// Maximum degree and Minimum Degree
	std::cout << max_degree << "," << min_degree << ",";
	// Average Degree
	std::cout << avg_degree << ",";
	// Average Degree Variance
	std::cout << avg_degree_variance << ",";
	// Global Clustering Coefficients
	std::cout << C_global<< ",";
	// Average Clustering Coefficients
	std::cout << C_avg << std::endl;
}

int main(int argc, char** argv) {
	test_network_info(argc, argv);
}