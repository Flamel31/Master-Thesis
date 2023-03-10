#include <gunrock/algorithms/algorithms.hxx>

using namespace gunrock;
using namespace memory;

void test_random_network(int num_arguments, char** argument_array) {
	if (num_arguments != 4) {
		std::cerr << "usage: ./bin/<program-name> num_vertices probability_ij folder_path" << std::endl;
		exit(1);
	}
	
	int num_vertices = atoi(argument_array[1]);
	float probability_ij = atof(argument_array[2]);
	
	if (probability_ij < 0 || probability_ij > 1) {
		std::cerr << "probability_ij should be between 0.0 and 1.0" << std::endl;
		exit(1);
	}
	
	// Define types
	using vertex_t = int;
	using edge_t = int;
	using weight_t = float;

	// IO
	std::string outpath = argument_array[3];
	// Setting random seed
	srand(time(NULL));

	using csr_t = format::csr_t<memory::memory_space_t::host, vertex_t, edge_t, weight_t>;
	csr_t csr;
	
	int last_count = 0;
	int count = 0;
	csr.row_offsets.push_back(count);
	for(vertex_t i = 0; i < num_vertices ; i++){
		last_count += count;
		count = 0;
		for(vertex_t j = 0; j < num_vertices ; j++){
			if(i == j) continue;
			// Random Value between 0.0 and 1.0
			float r = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
			if(r <= probability_ij){
				// Random Weight between 1.0 and 64.0
				weight_t w = 1 + static_cast <weight_t> (rand()) /( static_cast <weight_t> (RAND_MAX/(63)));
				csr.column_indices.push_back(j);
				csr.nonzero_values.push_back(w);
				count++;
			}			
		}
		csr.row_offsets.push_back(last_count+count);
	}
	
	csr.number_of_rows = num_vertices;
	csr.number_of_columns = num_vertices;
	csr.number_of_nonzeros = csr.nonzero_values.size();

	std::cout << "Generating network with " << num_vertices << " vertices and probability of an edge between i and j of " << probability_ij << std::endl;
	std::cout << "csr.number_of_rows     = " << csr.number_of_rows << std::endl;
	std::cout << "csr.number_of_columns  = " << csr.number_of_columns << std::endl;
	std::cout << "csr.number_of_nonzeros = " << csr.number_of_nonzeros << std::endl;
	std::cout << "writing to             = " << outpath << std::endl;

	csr.write_binary(outpath);
}

int main(int argc, char** argv) {
	test_random_network(argc, argv);
}