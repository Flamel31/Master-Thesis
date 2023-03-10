#pragma once

#include <gunrock/container/vector.hxx>
#include <gunrock/memory.hxx>

namespace gunrock {
namespace format {

using namespace memory;

/**
 * @brief Compressed Sparse Column (CSC) format.
 *
 * @tparam index_t
 * @tparam offset_t
 * @tparam value_t
 */
template <memory_space_t space,
          typename index_t,
          typename offset_t,
          typename value_t>
struct csc_t {
  index_t number_of_rows;
  index_t number_of_columns;
  index_t number_of_nonzeros;

  vector_t<offset_t, space> column_offsets;  // Aj
  vector_t<index_t, space> row_indices;      // Ap
  vector_t<value_t, space> nonzero_values;   // Ax

  csc_t()
      : number_of_rows(0),
        number_of_columns(0),
        number_of_nonzeros(0),
        column_offsets(),
        row_indices(),
        nonzero_values() {}

  csc_t(index_t r, index_t c, index_t nnz)
      : number_of_rows(r),
        number_of_columns(c),
        number_of_nonzeros(nnz),
        column_offsets(c + 1),
        row_indices(nnz),
        nonzero_values(nnz) {}

  ~csc_t() {}
  
    /**
   * @brief Copy constructor.
   * @param rhs
   */
  template <typename _csc_t>
  csc_t(const _csc_t& rhs)
      : number_of_rows(rhs.number_of_rows),
        number_of_columns(rhs.number_of_columns),
        number_of_nonzeros(rhs.number_of_nonzeros),
        column_offsets(rhs.column_offsets),
        row_indices(rhs.row_indices),
        nonzero_values(rhs.nonzero_values) {}
  
  /**
   * @brief Convert a Coordinate Sparse Format into Compressed Sparse Row
   * Format.
   *
   * @tparam index_t
   * @tparam offset_t
   * @tparam value_t
   * @param coo
   * @return csc_t<space, index_t, offset_t, value_t>&
   */
  csc_t<space, index_t, offset_t, value_t> from_coo(
      const coo_t<memory_space_t::host, index_t, offset_t, value_t>& coo) {
    number_of_rows = coo.number_of_rows;
    number_of_columns = coo.number_of_columns;
    number_of_nonzeros = coo.number_of_nonzeros;

    // Allocate space for vectors
    vector_t<offset_t, memory_space_t::host> Ap(number_of_columns + 1);
    vector_t<index_t, memory_space_t::host> Aj(number_of_nonzeros);
    vector_t<value_t, memory_space_t::host> Ax(number_of_nonzeros);

    // compute number of non-zero entries per column of A.
    for (offset_t n = 0; n < number_of_nonzeros; ++n) {
      ++Ap[coo.column_indices[n]];
    }

    // cumulative sum the nnz per column to get column_offsets[].
    for (index_t i = 0, sum = 0; i < number_of_columns; ++i) {
      index_t temp = Ap[i];
      Ap[i] = sum;
      sum += temp;
    }
    Ap[number_of_columns] = number_of_nonzeros;

    // write coordinate column indices and nonzero values into CSC's
    // column indices and nonzero values.
    for (offset_t n = 0; n < number_of_nonzeros; ++n) {
      index_t column = coo.column_indices[n];
      index_t dest = Ap[column];

      Aj[dest] = coo.row_indices[n];
      Ax[dest] = coo.nonzero_values[n];

      ++Ap[column];
    }

    for (index_t i = 0, last = 0; i <= number_of_columns; ++i) {
      index_t temp = Ap[i];
      Ap[i] = last;
      last = temp;
    }

    // If returning a device csc_t, move coverted data to device.
    column_offsets = Ap;
    row_indices = Aj;
    nonzero_values = Ax;

    return *this;  // CSC representation (with possible duplicates)
  }

};  // struct csc_t

}  // namespace format
}  // namespace gunrock
