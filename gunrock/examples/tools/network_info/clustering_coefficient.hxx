#include <vector>

#include <thrust/host_vector.h>

namespace clustering_coefficient {

	using namespace std;

	template <typename csr_t, typename vertex_t, typename edge_t, typename weight_t>
	void run(csr_t& csr, double& C_global, double& C_avg) {
		// Copy data to CPU
		thrust::host_vector<edge_t> _row_offsets(csr.row_offsets);
		thrust::host_vector<vertex_t> _column_indices(csr.column_indices);
		thrust::host_vector<weight_t> _nonzero_values(csr.nonzero_values);

		edge_t* row_offsets = _row_offsets.data();
		vertex_t* column_indices = _column_indices.data();
		weight_t* nonzero_values = _nonzero_values.data();
		
		// Data structure needed
		thrust::host_vector<int> _num(csr.number_of_rows);
		thrust::host_vector<int> _den(csr.number_of_rows);
		
		int* num = _num.data();
		int* den = _den.data();
		
		for (vertex_t i = 0; i < csr.number_of_rows; i++){
			num[i] = 0;
			den[i] = 0;
		}

		for (vertex_t i = 0; i < csr.number_of_rows; i++){
			den[i] = row_offsets[i + 1] - row_offsets[i];
			// For each neighbors of i
			for (vertex_t offset_i = row_offsets[i]; offset_i < row_offsets[i + 1]; offset_i++) {
				vertex_t j = column_indices[offset_i];
				// For each neighbors of j
				for (vertex_t offset_j = row_offsets[j]; offset_j < row_offsets[j + 1]; offset_j++) {
					vertex_t k = column_indices[offset_j];
					// For each neighbors of k
					for (vertex_t offset_k = row_offsets[k]; offset_k < row_offsets[k + 1] && column_indices[offset_k] <= i; offset_k++) {
						// Triangle Found
						if(column_indices[offset_k] == i) num[i] += 1;
					}
				}
			}
		}
		
		double sum_num = 0;
		double sum_den = 0;
		for (vertex_t i = 0; i < csr.number_of_rows; i++){
			double curr_den = den[i] * (den[i] - 1);
			sum_num += num[i];
			sum_den += curr_den;
			if(den[i] != 0 && den[i] != 1)
				C_avg = num[i] / curr_den;
		}
		C_global = sum_num / sum_den;
		C_avg = C_avg / csr.number_of_rows;
	}

}  // namespace sssp_cpu
