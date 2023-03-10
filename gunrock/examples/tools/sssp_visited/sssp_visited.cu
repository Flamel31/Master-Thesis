#include <gunrock/algorithms/sssp.hxx>
// Reference implementations
#include "sssp_cpu.hxx"
using namespace gunrock;
using namespace memory;

void test_sssp(int num_arguments, char** argument_array) {
	if (num_arguments < 2) {
		std::cerr << "usage: ./bin/<program-name> filename.mtx [num_runs]" << std::endl;
		exit(1);
	}

	// Define types
	using vertex_t = int;
	using edge_t = int;
	using weight_t = float;
	using csr_t = format::csr_t<memory_space_t::host, vertex_t, edge_t, weight_t>;

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
	
	// Number of runs
	int num_runs = (num_arguments >= 3) ? atoi(argument_array[2]) : 10;
	
	// Params and memory allocation
	auto rng_seed = time(NULL);
	
	vertex_t n_vertices = csr.number_of_rows;
	edge_t n_edges = csr.number_of_nonzeros;
	vertex_t single_source = 0;

	// CPU Output Vectors
	thrust::host_vector<weight_t> distances(n_vertices);
	thrust::host_vector<float> visited(n_vertices);

	// Taking times
	srand(rng_seed);
	std::cout << "Dijkstra,SLF-LLL" << std::endl;
	for (auto i = 0; i < num_runs; i++){
		single_source = rand() % n_vertices;
		// Dijkstra Algorithm
		std::cout << sssp_cpu::dijkstra<vertex_t, edge_t, weight_t>(csr.row_offsets.data(), csr.column_indices.data(), csr.nonzero_values.data(),
			n_vertices, single_source, distances.data(), visited.data()) << ",";
		// SLF-LLL Algorithm
		std::cout << sssp_cpu::slflll<vertex_t, edge_t, weight_t>(csr.row_offsets.data(), csr.column_indices.data(), csr.nonzero_values.data(),
			n_vertices, single_source, distances.data(), visited.data()) << std::endl;
	}
	
	// Errors count
	/*int n_errors = util::compare(distances.data().get(), h_distances.data(), n_vertices);
	if(n_errors > 0)
		std::cout << "Number of errors : " << n_errors << std::endl;*/
	
	// Errors count
	/*n_errors = util::compare(distances.data().get(), h_distances.data(), n_vertices);
	if(n_errors > 0)
		std::cout << "Number of errors : " << n_errors << std::endl;*/
}

int main(int argc, char** argv) {
	test_sssp(argc, argv);
}