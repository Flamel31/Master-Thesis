#include <chrono>
#include <vector>
#include <queue>

#include <thrust/host_vector.h>

namespace sssp_cpu_parallel {

	using namespace std;
	using namespace std::chrono;	
	
	template <typename csr_t, typename vertex_t, typename edge_t, typename weight_t>
	float run(csr_t& csr, vertex_t& single_source, weight_t* distances, vertex_t* predecessors,int n_process) {
		using csc_t = format::csr_t<memory_space_t::host, vertex_t, edge_t, weight_t>;
		// Copy data to CPU using csc format
		csc_t csc;
		csc.from_csr(csr);

		edge_t* column_offsets = csc.column_offsets.data();
		vertex_t* row_indices = csc.row_indices.data();
		weight_t* nonzero_values = csc.nonzero_values.data();
		
		// Divide the workload between the available number of processes
		int processes_offsets[n_process+1];
		int workload = ; 
		
		omp_set_num_threads(n_process);
		
		#pragma omp parallel for
		for (vertex_t i = 0; i < csc.number_of_rows; i++)
			distances[i] = std::numeric_limits<weight_t>::infinity();

		distances[single_source] = 0;
		
		auto t_start = high_resolution_clock::now();
		
		#pragma omp parallel
		{
			int rank = omp_get_thread_num();
			vertex_t start = csc.number_of_nonzeros * (rank / n_process);
			vertex_t end = csc.number_of_nonzeros * ((rank+1) / n_process);
			for (int i = 0; i < csc.number_of_rows - 1; i++){
				for (vertex_t v = start; v < end; v++){
					for (vertex_t offset = column_offsets[v]; offset < column_offsets[v+1]; offset++) {
						vertex_t u = row_indices[offset];
						weight_t new_dist = distances[u] + nonzero_values[offset];
						if (new_dist < distances[v]) {
							distances[v] = new_dist;
						}
					}
				}
			}
		}
		
		auto t_stop = high_resolution_clock::now();
		auto elapsed = duration_cast<microseconds>(t_stop - t_start).count();
		return (float)elapsed / 1000;
	}
}
