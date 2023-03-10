#include <gunrock/algorithms/sssp.hxx>
#include <unistd.h>
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
	
	// Number of runs
	int num_runs = (num_arguments >= 3) ? atoi(argument_array[2]) : 10;
	
	// Params and memory allocation
	auto rng_seed = time(NULL);
	
	vertex_t n_vertices = G.get_number_of_vertices();
	edge_t n_edges = G.get_number_of_edges();
	vertex_t single_source = 0;

	// GPU Output Vectors
	thrust::device_vector<weight_t> distances(n_vertices);
	thrust::device_vector<vertex_t> predecessors(n_vertices);
	// CPU Output Vectors
	thrust::host_vector<weight_t> h_distances(n_vertices);
	thrust::host_vector<vertex_t> h_predecessors(n_vertices);
	
	// Copy data to CPU
	thrust::host_vector<edge_t> _row_offsets(csr.row_offsets);
	thrust::host_vector<vertex_t> _column_indices(csr.column_indices);
	thrust::host_vector<weight_t> _nonzero_values(csr.nonzero_values);

	// Taking times
	srand(rng_seed);
	std::cout << "Gunrock,Dijkstra,SLF-LLL" << std::endl;
	for (auto i = 0; i < num_runs; i++){
		single_source = rand() % n_vertices;
		// GPU Run
		// Gunrock Algorithm
		std::cout << gunrock::sssp::run(G, single_source, distances.data().get(),predecessors.data().get()) << ",";
		// CPU Runs
		// Dijkstra Algorithm
		std::cout << sssp_cpu::dijkstra<vertex_t, edge_t, weight_t>(_row_offsets.data(), _column_indices.data(), _nonzero_values.data(),
			n_vertices, single_source, h_distances.data(), h_predecessors.data()) << ",";
		// SLF-LLL Algorithm
		std::cout << sssp_cpu::slflll<vertex_t, edge_t, weight_t>(_row_offsets.data(), _column_indices.data(), _nonzero_values.data(),
			n_vertices, single_source, h_distances.data(), h_predecessors.data()) << std::endl;
		usleep(1000000);
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