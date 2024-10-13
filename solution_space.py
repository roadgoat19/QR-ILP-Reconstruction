import galois

def find_pivots(reduced_matrix):
    pivots = []
    row_index = 0
    for col_index in range(len(reduced_matrix[0])):
        if row_index == len(reduced_matrix):
            break
        if reduced_matrix[row_index][col_index] != 0:
            pivots.append(col_index)
            row_index += 1
    
    return pivots

# Note: matrix and b should be lists, not GF matrices
def solution_space(matrix, b):

    GF = galois.GF(256)

    # matrix = [[1, 0, 1],
    #         [0, 1, 1]]

    # b = [1, 2]

    num_cols = len(matrix[0])

    augmented = GF([matrix[i] + [b[i]] for i in range(len(matrix))])

    augmented_reduced = augmented.row_reduce(ncols = num_cols)
    reduced = GF([[augmented_reduced[row][col] for col in range(len(matrix[0]))] for row in range(len(augmented))])
    reduced_b = GF([augmented_reduced[row][len(matrix[0])] for row in range(len(augmented_reduced))])

    # print(augmented_reduced)
    # print(reduced)
    # print(reduced_b)

    shift = []

    pivot_columns = find_pivots(reduced)

    row_index = 0
    for col_index in range(num_cols):
        if col_index in pivot_columns:
            shift.append(reduced_b[row_index])
            row_index += 1
        else:
            shift.append(0)

    # print(shift)

    null_space = reduced.null_space().transpose()

    # print(null_space)

    return GF(shift), null_space