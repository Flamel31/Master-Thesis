#include <gunrock/algorithms/algorithms.hxx>
// Reference implementations
#include "sssp_cpu.hxx"
using namespace gunrock;
using namespace memory;

void test_sssp(int num_arguments, char** argument_array) {
	if (num_arguments < 2) {
		std::cerr << "usage: ./bin/<program-name> filename.mtx [num_threads] [num_runs]" << std::endl;
		exit(1);
	}

	// Define types
	using vertex_t = int;
	using edge_t = int;
	using weight_t = float;
	using csc_t = format::csc_t<memory_space_t::host, vertex_t, edge_t, weight_t>;
	using csr_t = format::csr_t<memory_space_t::host, vertex_t, edge_t, weight_t>;
	
	// IO
	csc_t csc;
	csr_t csr;
	std::string filename = argument_array[1];
	if (util::is_market(filename)) {
		io::matrix_market_t<vertex_t, edge_t, weight_t> mm;
		csc.from_coo(mm.load(filename));
		csr.from_coo(mm.load(filename));
	} else if (util::is_binary_csr(filename)) {		
		//csr.read_binary(filename);
		std::cerr << "CSR Binary file not implemented yet." << std::endl;
		exit(1);
	} else {
		std::cerr << "Unknown file format: " << filename << std::endl;
		exit(1);
	}
	
	// Number of threads
	int num_threads = (num_arguments >= 3) ? atoi(argument_array[2]) : 64;
	
	// Number of runs
	int num_runs = (num_arguments >= 4) ? atoi(argument_array[3]) : 10;
	
	// Params and memory allocation
	auto rng_seed = time(NULL);
	
	vertex_t n_vertices = csc.number_of_columns;
	vertex_t single_source = 0;
	
	// CPU Output Vectors
	thrust::host_vector<weight_t> distances(n_vertices);
	thrust::host_vector<vertex_t> predecessors(n_vertices);
	
	// Taking times
	srand(rng_seed);
	std::cout << "Bellman-Ford Parallel (csc) " << num_threads << " threads,";
	std::cout << "Bellman-Ford Parallel (csr) " << num_threads << " threads" << std::endl;
	for (auto i = 0; i < num_runs; i++){
		single_source = rand() % n_vertices;
		std::cout << sssp_cpu::run_csc<csc_t, vertex_t, edge_t, weight_t>(csc, single_source, distances.data(), 
			predecessors.data(), num_threads) << ",";
		std::cout << sssp_cpu::run_csr<csr_t, vertex_t, edge_t, weight_t>(csr, single_source, distances.data(), 
			predecessors.data(), num_threads) << std::endl;
	}
	
	/*
	// Errors count
	int n_errors = util::compare(distances_csc.data(), distances_csr.data(), n_vertices);
	if(n_errors > 0){
		std::cout << "Number of errors : " << n_errors << std::endl;
		print::head(distances_csc,100,"Csc distances");
		print::head(distances_csr,100,"Csr distances");
	}
	*/
}

int main(int argc, char** argv) {
	test_sssp(argc, argv);
}
