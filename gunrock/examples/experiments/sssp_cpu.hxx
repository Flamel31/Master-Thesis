#include <chrono>
#include <vector>
#include <queue>

#include <thrust/host_vector.h>
#include <omp.h>

namespace sssp_cpu {

	using namespace std;
	using namespace std::chrono;	
	
	template <typename csc_t, typename vertex_t, typename edge_t, typename weight_t>
	float run_csc(csc_t& csc, vertex_t& single_source, weight_t* distances, vertex_t* predecessors, int& threads) {
		// Arrays used to keep track of the last modified vertices		
		thrust::host_vector<bool> frontier(csc.number_of_columns);
		thrust::host_vector<bool> new_frontier(csc.number_of_columns);
		
		// Boolean used to check for early termination
		bool exit = false;
		
		omp_set_num_threads(threads);
		
		#pragma omp parallel for
		for (vertex_t i = 0; i < csc.number_of_columns; i++){
			distances[i] = std::numeric_limits<weight_t>::infinity();
			frontier[i] = false;
			new_frontier[i] = false;
		}
		
		distances[single_source] = 0;
		frontier[single_source] = true;
		
		auto t_start = high_resolution_clock::now();
		
		#pragma omp parallel
		{
			double rank = omp_get_thread_num();
			vertex_t start = csc.number_of_columns * (rank / threads);
			vertex_t end = csc.number_of_columns * ((rank+1) / threads);
			for (int i = 0; i < (csc.number_of_columns - 1) && !exit; i++){
				for (vertex_t v = start; v < end; v++){
					for (vertex_t offset = csc.column_offsets[v]; offset < csc.column_offsets[v+1]; offset++) {
						vertex_t u = csc.row_indices[offset];
						// If u has not been modified the last iteration then we can skip it
						if (!frontier[u]) continue;
						weight_t new_dist = distances[u] + csc.nonzero_values[offset];
						if (new_dist < distances[v]){
							distances[v] = new_dist;
							new_frontier[v] = true;
						}
					}
				}
				#pragma omp barrier
				#pragma omp single
				{
					exit = true;
					// Check for early exit condition
					for (vertex_t v = 0; v < csc.number_of_columns; v++){
						exit &= !new_frontier[i];
						frontier[i] = new_frontier[i];
						new_frontier[i] = false;			
					}
				}
			}
		}
		
		auto t_stop = high_resolution_clock::now();
		auto elapsed = duration_cast<microseconds>(t_stop - t_start).count();
		return (float)elapsed / 1000;
	}
	
	template <typename csr_t, typename vertex_t, typename edge_t, typename weight_t>
	float run_csr(csr_t& csr, vertex_t& single_source, weight_t* distances, vertex_t* predecessors, int& threads) {
		// Arrays used to keep track of the last modified vertices		
		thrust::host_vector<bool> frontier(csr.number_of_rows);
		thrust::host_vector<bool> new_frontier(csr.number_of_rows);
		
		// Boolean used to check for early termination
		bool exit = false;
		
		omp_set_num_threads(threads);
		
		#pragma omp parallel for
		for (vertex_t i = 0; i < csr.number_of_rows; i++){
			distances[i] = std::numeric_limits<weight_t>::infinity();
			frontier[i] = false;
			new_frontier[i] = false;
		}
		
		distances[single_source] = 0;
		frontier[single_source] = true;	
		
		auto t_start = high_resolution_clock::now();
		
		for (int i = 0; i < (csr.number_of_rows - 1) && !exit; i++){
			for (vertex_t u = 0; u < csr.number_of_rows; u++){
				// If u has not been modified the last iteration then we can skip it
				if (!frontier[u]) continue;
				#pragma omp parallel for
				for (vertex_t offset = csr.row_offsets[u]; offset < csr.row_offsets[u+1]; offset++) {
					vertex_t v = csr.column_indices[offset];
					weight_t new_dist = distances[u] + csr.nonzero_values[offset];
					if (new_dist < distances[v]){
						distances[v] = new_dist;
						new_frontier[v] = true;
					}
				}
			}
			// Check for early exit condition
			exit = true;
			#pragma omp parallel for reduction(&&:exit)
			for (vertex_t v = 0; v < csr.number_of_rows; v++){
				exit &= !new_frontier[i];
				frontier[i] = new_frontier[i];
				new_frontier[i] = false;			
			}
		}
		
		auto t_stop = high_resolution_clock::now();
		auto elapsed = duration_cast<microseconds>(t_stop - t_start).count();
		return (float)elapsed / 1000;
	}
}
