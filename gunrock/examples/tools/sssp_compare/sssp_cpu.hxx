#pragma once

#include <chrono>
#include <vector>
#include <deque>
#include <queue>

#include <thrust/host_vector.h>

namespace sssp_cpu {

	using namespace std;
	using namespace std::chrono;

	template <typename vertex_t, typename weight_t>
	class prioritize {
		public:
		bool operator()(pair<vertex_t, weight_t>& p1, pair<vertex_t, weight_t>& p2) {
			return p1.second > p2.second;
		}
	};

	template <typename vertex_t, typename edge_t, typename weight_t>
	float dijkstra(edge_t* row_offsets, vertex_t* column_indices, weight_t* nonzero_values,
		vertex_t& number_of_vertices, vertex_t& single_source, weight_t* distances, vertex_t* predecessors) {

		for (vertex_t i = 0; i < number_of_vertices; i++)
			distances[i] = std::numeric_limits<weight_t>::infinity();

		distances[single_source] = 0;

		priority_queue<pair<vertex_t, weight_t>,std::vector<pair<vertex_t,weight_t>>,prioritize<vertex_t,weight_t>> pq;
		pq.push(make_pair(single_source, 0.0));
		auto t_start = high_resolution_clock::now();
		while (!pq.empty()) {
			pair<vertex_t, weight_t> curr = pq.top();
			pq.pop();

			vertex_t curr_node = curr.first;
			weight_t curr_dist = curr.second;

			vertex_t start = row_offsets[curr_node];
			vertex_t end = row_offsets[curr_node + 1];

			for (vertex_t offset = start; offset < end; offset++) {
				vertex_t neib = column_indices[offset];
				weight_t new_dist = curr_dist + nonzero_values[offset];
				if (new_dist < distances[neib]) {
					distances[neib] = new_dist;
					pq.push(make_pair(neib, new_dist));
				}
			}
		}

		auto t_stop = high_resolution_clock::now();
		auto elapsed = duration_cast<microseconds>(t_stop - t_start).count();
		return (float)elapsed / 1000;
	}
	
	template <typename vertex_t, typename edge_t, typename weight_t>
	float slflll(edge_t* row_offsets, vertex_t* column_indices, weight_t* nonzero_values,
		vertex_t& number_of_vertices, vertex_t& single_source, weight_t* distances, vertex_t* predecessors) {
		// Boolmap used to track on queue vertices
		thrust::host_vector<bool> _in_queue(number_of_vertices);
		bool* in_queue = _in_queue.data();
		
		// Init distances from vertices to inf
		for (vertex_t i = 0; i < number_of_vertices; i++){
			distances[i] = std::numeric_limits<weight_t>::infinity();
			in_queue[i] = false;
		}
		
		// Init distance from source to 0
		distances[single_source] = 0;
		in_queue[single_source] = true;
		
		// Init total weight to 0
		weight_t total_w = 0;
		weight_t avg_w = 0;
		
		// Double ended queque structure 
		deque<vertex_t> dq;
		// Push source vertex into the deque
		dq.push_front(single_source);
		
		auto t_start = high_resolution_clock::now();
		
		while (!dq.empty()) {
			// LLL heuristic: pick the first node with weight less than the queue average
			avg_w = total_w / dq.size();
			vertex_t curr_node = dq.front();
			dq.pop_front();
			for(int i = 0; (distances[curr_node] > avg_w) && (i < dq.size()); i++){
				dq.push_back(curr_node);
				curr_node = dq.front();
				dq.pop_front();
			}
			// update total weight
			in_queue[curr_node] = false;
			total_w -= distances[curr_node];
			
			// visit neighbors to propagate distances
			vertex_t start = row_offsets[curr_node];
			vertex_t end = row_offsets[curr_node + 1];
			for (vertex_t offset = start; offset < end; offset++) {
				vertex_t neib = column_indices[offset];
				weight_t new_dist = distances[curr_node] + nonzero_values[offset];
				if (new_dist < distances[neib]) {
					// check if the node is already in the queue
					if(in_queue[neib]){
						// node already in queue, update total weight
						total_w = total_w - distances[neib] + new_dist;
					}else{
						// add neighbor to queue with SLF heuristic
						if(dq.empty() || new_dist < distances[dq.front()]){
							dq.push_front(neib);
						}else{
							dq.push_back(neib);
						}
						in_queue[neib] = true;
						total_w += new_dist;
					}
					// propagate distance
					distances[neib] = new_dist;
				}
			}
		}

		auto t_stop = high_resolution_clock::now();
		auto elapsed = duration_cast<microseconds>(t_stop - t_start).count();
		return (float)elapsed / 1000;
	}

}  // namespace sssp_cpu
