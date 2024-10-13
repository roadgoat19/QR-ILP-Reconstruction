from deblur import *
from relaxed_directional_sums import SumCalculator
from ilp_solver import solve_relaxed_message as solve
from reedsolo import *

def set_up_sums(matrix, size):
    sums = SumCalculator(size, matrix)
    sums.computeAllDirectionalSums()
    return sums

def block_coords(byte, block, each_byte):
    return [qr_coords_message((2 * byte + block - 1) * 8 + i) for i in range(each_byte)]

def relax_directional_sums(sums, fixed_bytes, each_byte = 8):
    
    for block in range(1, 3):
        for byte in fixed_bytes[block - 1]:
            for point in block_coords(byte = byte, block = block, each_byte = each_byte):
                sums.relaxDirectionalSums(point)
    
def fill_in(solution, fixed_bytes, mask):

    rs = RSCodec(22)

    for block in range(1, 3):

        block_message = []
        
        for block_index in range(35):

            byte = 0

            for byte_index in range(8):

                byte = byte << 1

                message_index = (2 * block_index + block - 1) * 8 + byte_index
                # print(message_index)
                row, col = qr_coords_message(message_index)

                solution_val = solution[row][col]
                byte += 0 if solution_val is None else int(solution_val == 0 if is_masked((row, col), mask) else solution_val)


            # print(byte)
            
            block_message.append(byte)
        
        _, decoded, _ = rs.decode(block_message, erase_pos = fixed_bytes[block - 1], only_erasures = True)

        for block_index in range(35):

            byte = decoded[block_index]
            
            for byte_index in range(8):
                message_index = (2 * block_index + block - 1) * 8 + byte_index
                row, col = qr_coords_message(message_index)
                bit = (byte >> 7) & 1
                solution[row][col] = int(bit == 0) if is_masked((row, col), mask) else bit
                byte = byte << 1



        

def main():

    global known_blacks, known_whites
    GF = galois.GF(256)
    init_tables()

    input = "./codes/high0.txt"
    blur_level = 3

    size, matrix = read_QR(input)

    mask = get_mask(matrix)
    ec = get_ec(matrix)
    print("Mask: %d; EC Level: %s" % (mask, ec))

    sums = set_up_sums(matrix, size)

    # Apply the low-pass filter
    directions_removed = blur(sums, blur_level=blur_level)

    # Apply the format information and error correction reductions
    apply_format_information(ec, mask, matrix)

    # Apply the fixed structure reduction
    reduce_data(sums, size)

    # Fixed stucuture and format reductions were correct
    assert reduced_structure_matches_original(matrix)

    n_bytes_changed = 6

    # Fix 11 bytes in each block
    block_1_fixed = list(range(n_bytes_changed))
    block_2_fixed = list(range(n_bytes_changed))
    fixed_bytes = [block_1_fixed, block_2_fixed]

    # Relax the directional sums and remove these variables
    
    relax_directional_sums(sums, fixed_bytes, each_byte = 1)

    # Solve the relaxed ILP

    solution = solve(sums.sumLibrary, size)

    fill_in(solution, fixed_bytes, mask)

    # Check if the solution matches the input

    n_left_out = sum([solution[i // 29][i % 29] is None for i in range(29 * 29)])
    matches = reduce(lambda x, y: x + y, [[solution[i][j] is None or int(solution[i][j]) == matrix[i][j] for i in range(size)] for j in range(size)], [])

    # fixed_count = len(known_blacks + known_whites)
    correct_count = 29 * 29 - sum(matches)
    print("Number wrong: %d; number determined: %d" % (correct_count, 29 * 29 - n_left_out))


    assert(all(matches))

    # Fill in the matrix with error correction.

if __name__ == "__main__":
    main()