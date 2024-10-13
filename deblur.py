import directionalsums as dsums
import itertools
from reedsolo import *
import reader
import numpy
import galois
from message_sequence import getModuleSequence
from ilp_solver import solve_ilp as solve
from functools import reduce
import alt_projection
import csv

known_whites = []
known_blacks = []
coord_to_index_map = None
index_to_coord_map = None

# Translate input file to binary matrix
def read_QR(input):

    file = open(input, "r")

    first_line = file.readline()
    size = int(first_line)
    # print(first_line)

    matrix = [[int(file.read(1)) for i in range(size)] for _ in range(size)]

    file.close()

    # print(matrix)

    return (size, matrix)

    #return reader.png_reader(input)

def get_mask(matrix):
    
    XOR_with = 0b101

    fst_row, fst_col = qr_coords_format(2)
    snd_row, snd_col = qr_coords_format(3)
    thrd_row, thrd_col = qr_coords_format(4)

    mask_bits = matrix[fst_row][fst_col] * 4
    mask_bits += matrix[snd_row][snd_col] * 2
    mask_bits += matrix[thrd_row][thrd_col]

    mask = mask_bits ^ XOR_with

    # print(mask)

    return mask

def get_ec(matrix):
    fst_row, fst_col = qr_coords_format(0)
    snd_row, snd_col = qr_coords_format(1)

    ec = (2 * matrix[fst_row][fst_col] + matrix[snd_row][snd_col])

    return ["high", "quart", "med", "low"][ec]

def set_up_sums(matrix, size):
    sums = dsums.SumCalculator(size, matrix)
    sums.computeAllDirectionalSums()
    return sums

# Calculate directional sums from a binary matrix representation of QR code
def directional_sums(signal, size):
    sum_calc = directional_sums.SumCalculator(size, signal)
    sum_calc.computeAllDirectionalSums()
    return sum_calc

# Apply low pass filter
# Blur level 0, 1, 2, ... where 0 is no blur
def blur(sums, blur_level = 0):
    
    # if blur_level is None:
    #     return sums

    directions_removed = 0

    for level in range(blur_level):
        directions_removed += sums.removeDirectionalSums(5 - level)

    return directions_removed

# From the qrcodegen library: size is between 21 and 177 (inclusive). This is equal to version * 4 + 17.
def version(size):
    return (size - 17) // 4

# vector addition of two coordinates
def add(p1, p2):
    return (p1[0] + p2[0], p1[1] + p2[1])

# Use fixed structure to reduce directional sums data
# All except the (4 * (version - 1), 8) bit is symmetric with respect to the main diagonal, so the order of coordinates didn't matter, but may not be consistent.
def reduce_data(sums, size):

    global known_blacks, known_whites

    version = (size - 17) // 4

    known_blacks += [(21, 8)]  

    # Handle finder patterns by updating known arrays:

    for corner, label in [((0, 0), "topleft"), ((0, size - 7), "topright"), ((size - 7, 0), "bottomleft")]:

        # corner is the coordinate of the top right corner of the larger black square

        blacks = []

        # middle black:
        # print(label)
        blacks += list(map(lambda pair: add(add(corner, (2, 2)), pair), itertools.product(range(3), range(3))))

        # outer black
        blacks += map(lambda n: add(corner, (0, n)), range(7))
        blacks += map(lambda n: add(corner, (n, 0)), range(1, 7))
        blacks += map(lambda n: add(corner, (6, n)), range(1, 7))
        blacks += map(lambda n: add(corner, (n, 6)), range(1, 6))

        match label:
            case "topleft":
                area_of_finder = [range(8), range(8)]
            case "bottomleft": 
                area_of_finder = [range(size - 8, size), range(8)]
            case "topright": 
                area_of_finder = [range(8), range(size - 8, size)]

        whites = [item for item in itertools.product(*area_of_finder) if item not in blacks] # the rest of the finder pattern is white

        # print(blacks)
        # print(whites)

        known_blacks += blacks
        known_whites += whites

    # Locations of alignment patterns algorithm from https://dev.to/maxart2501/let-s-develop-a-qr-code-generator-part-viii-different-sizes-1e0e

    n = version // 7 + 2 # Number of tracks

    first_track = 6
    last_track = size - 7

    distance = (((last_track - first_track) // (n - 1)) + 1) // 2 * 2

    # print(distance)

    last = last_track

    tracks = []

    while last > first_track:
        tracks = [last] + tracks
        last -= distance
    
    tracks = [first_track] + tracks

    

    for (i, j) in itertools.product(tracks, tracks):
        if (i, j) == (first_track, first_track) or (i, j) == (first_track, last_track) or (i, j) == (last_track, first_track):
            None
        else:
            topleft = i - 2, j - 2

            whites = [add(topleft, (1, 2)), add(topleft, (3, 2))] 
            blacks = [add(topleft, (2, 2))] 


            blacks += map(lambda n: add(topleft, (0, n)), range(5))
            blacks += map(lambda n: add(topleft, (n, 0)), range(1, 5))
            blacks += map(lambda n: add(topleft, (4, n)), range(1, 5))
            blacks += map(lambda n: add(topleft, (n, 4)), range(1, 4))

            whites += map(lambda n: add(topleft, (1 + n, 1)), range(3))
            whites += map(lambda n: add(topleft, (1 + n, 3)), range(3))

            known_whites += whites
            known_blacks += blacks


    # timing patterns (I don't know if this is compatible with the alignment patterns for larger (size > 29) QR codes)
            
    known_blacks += map(lambda n: (6, n), range(8, size - 7, 2))
    known_blacks += map(lambda n: (n, 6), range(8, size - 7, 2))

    known_whites += map(lambda n: (6, n), range(9, size - 8, 2)) 
    known_whites += map(lambda n: (n, 6), range(9, size - 8, 2))

    # Intersection is empty
    for item in known_blacks: assert item not in known_whites
    for item in known_whites: assert item not in known_blacks

    for pair in known_whites:
        sums.adjustDirectionalSums(pair, 0)

    for pair in known_blacks:
        sums.adjustDirectionalSums(pair, 1)

    # map(lambda pair: sums.adjustDirectionalSums(pair, sums.sumLibrary, 0), known_whites)
    # map(lambda pair: sums.adjustDirectionalSums(pair, sums.sumLibrary, 1), known_blacks)

    # print("tracks: ", tracks)
    # print("known_whites: ", known_whites)
    # print("known_blacks: ", known_blacks)

def reduced_structure_matches_original(matrix):
    return (all([matrix[x][y] == 1 for x, y in known_blacks]) and
            all([matrix[x][y] == 0 for x, y in known_whites]))


# The cordinates in the QR_code of the m'th message bit (29 x 29 QR code)
def qr_coords_message(m, size = 29):
    global index_to_coord_map
    if index_to_coord_map is None:
        sequence = getModuleSequence(size)
        index_to_coord_map = {index : point for point, index in zip(sequence, range(len(sequence)))}
    return index_to_coord_map.get(m)

# The coordinates in the QR_code of the i'th format bit 
def qr_coords_format(i, size = 29):
    horz_coords = list(range(0, 6)) + [7] + list(range(size - 8, size))
    return (8, horz_coords[i])

def format_bit(point, size = 29):
    for i in range(15):
        if qr_coords_format(i) == point:
            return i
    return None

# returns m such that qr_cords_message(m) = point (29 x 29 QR code)
def message_bit(point, size = 29):
    global coord_to_index_map
    if coord_to_index_map is None:
        sequence = getModuleSequence(size)
        coord_to_index_map = {point : index for point, index in zip(sequence, range(len(sequence)))}
    return coord_to_index_map.get(point)


# indicates whether the point is masked under the given mask (29 x 29 QR code)
def is_masked(point, mask):
    row, column = point
    match mask:
        case 0:
            return (row + column) % 2 == 0
        case 1:	
            return row % 2 == 0
        case 2:
            return column % 3 == 0
        case 3:	
            return (row + column) % 3 == 0
        case 4:	
            return (row // 2 + column // 3) % 2 == 0
        case 5:	
            return row * column % 2 + row * column % 3 == 0
        case 6:	
            return ((row * column) % 2 + row * column % 3) % 2 == 0
        case 7:	
            return ((row + column) % 2 + row * column % 3) % 2 == 0


# Sets up linear equation Ax=b for the syndromes of the message
def apply_message_syndromes(n, k, mask):
    init_tables()
    char_bit = 8
    # sets up matrix x

    if k < 36:
        syndromes = [[gf_pow(2, ( (char_bit - 1 - m) % char_bit + j * (n + k - (m // char_bit) - 1))) for m in range(char_bit * (n + k))] for j in range(k)]

    else:
        block_1_syndromes = [[gf_pow(2, ( (char_bit - 1 - (m - 8 * (m // 16))) % char_bit + j * (n + k - ((m - 8 * (m // 16)) // char_bit) - 1))) if m % 16 < 8 else 0 for m in range(char_bit * (n + k))] for j in range(k // 2)]
        block_2_syndromes = [[gf_pow(2, ( (char_bit - 1 - (m - 8 * (m // 16))) % char_bit + j * (n + k - ((m - 8 * (m // 16)) // char_bit) - 1))) if m % 16 >= 8 else 0 for m in range(char_bit * (n + k))] for j in range(k // 2)]

        syndromes = block_1_syndromes + block_2_syndromes


    
    b = []

    # if bit m is masked, then we add A_m,j to b_j

    for j in range(k):
        sum = 0
        for m in range(char_bit * (n + k)):
            if is_masked(qr_coords_message(m), mask):
                sum = gf_add(sum, syndromes[j][m])
        b.append(sum)

    return syndromes, b
    
    
    exit()

    GF = galois.GF(2 ** char_bit)

    gf_mat = GF(syndromes) # form the augmented matrix

    print(gf_mat)

    reduced = gf_mat.row_reduce()

    print(reduced)




def galois_directional_sums(sums, n):

    sum_library = sums.sumLibrary
    
    b = []
    matrix = []
    # for start, slope in sum_library.keys():
    #     line, sum = sum_library[(start, slope)]
    for line, sum in sum_library.values():
        matrix_row = [int((coord // n, coord % n) in line) for coord in range(n * n)]
        # print(matrix_row)
        
        b.append(sum % 2)
        matrix.append(matrix_row)

    return matrix, b

    # print(matrix)
    # print(len(matrix[0]))

    # non_augmented = [[matrix[j][i] for i in range(n * n)] for j in range(len(matrix))]

    # qr_code = sums.matrix

    # # Ax = 
    # b = numpy.matmul(numpy.array(non_augmented), [qr_code[coord // n][coord % n] for coord in range(n * n)])
    # print(b)

    # assert all([b[i] == matrix[i][n * n] for i in range(len(b))])

def gf_linear_system(sums, size, n, k, mask, include_ec = True):
    sum_matrix, sums_b = galois_directional_sums(sums, size)
    message_matrix, message_b = apply_message_syndromes(n, k, mask)
    
    full_system = message_matrix if include_ec else []
    # full_system = []

    for row_number in range(len(sum_matrix)):
        matrix_row = []
        for message_cord in range(len(message_matrix[0])):
            row, col = qr_coords_message(message_cord)
            matrix_row.append(sum_matrix[row_number][29 * row + col])
        full_system.append(matrix_row)

    return full_system, message_b + sums_b
    # return full_system, sums_b
            

# def gf_linear_system(sums, size, n, k, mask):
#     sum_matrix, sum_b = galois_directional_sums(sums, size)
#     message_matrix, message_b = apply_message_syndromes(n, k, mask)
#     # format_matrix = apply_format_syndromes()

#     print("sum_matrix: %d x %d" % (len(sum_matrix), len(sum_matrix[0])))
#     print("message_matrix: %d x %d" % (len(message_matrix), len(message_matrix[0])))

#     # full_system = sum_matrix
#     full_system = []
    

#     message_length = len(message_matrix[0])

#     for row_number in range(len(message_matrix)):
#         row = []
#         for coord in range(29 * 29):
#             point = (coord // 29, coord % 29)
#             message_coord = message_bit(point)
#             if message_coord is not None:
#                 # print(point,message_coord)
#                 row.append(message_matrix[row_number][message_coord])
#             else:
#                 row.append(0)
#         full_system.append(row)

#     # format_length = 15

#     # for row_number in len(format_matrix):
#     #     row = []
#     #     for coord in range(29 * 29):
#     #         point = (coord // 29, coord % 29)
#     #         format_coord = format_bit(point)
#     #         if format_coord is not None:
#     #             row.append(format_matrix[row_number][format_coord])
#     #         else:
#     #             row.append(0)
#     #     row.append(format_matrix[row_number][format_length])
#     #     full_system.append(row)
        

#     # print(full_system)

#     return full_system, sum_b + message_b

def test_gf_system(A, b, input_matrix):

    GF = galois.GF(256)

    # x = [input_matrix[i // 29][i % 29] for i in range(29 * 29)]
    x = []

    message_bit(0)
    # print(coord_to_index_map.keys()) # Seems to be in the correct order

    for row, col in coord_to_index_map.keys():
        x.append(input_matrix[row][col])


    # gf_A = GF(A)
    gf_x = GF(x)

    actual_b = numpy.matmul(A, gf_x)

    correct_count = 0
    for i in range(len(b)):
        # print("actual: %d; expected: %d" % (actual_b[i], b[i]))
        if b[i] == actual_b[i]:
            correct_count += 1
        else:
            print("correct_count: %d" % correct_count)
            assert(False)
    print("Correct row count: %d; total rows: %d" % (correct_count, len(b)))

    assert(all([b[i] == actual_b[i] for i in range(len(b))]))

def apply_format_syndromes():

    format_generator_poly = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]
    # What the format poly is XORed with before its placement
    format_mask = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]

    format_zeros = list(filter(lambda x: gf_poly_eval(format_generator_poly, x) == 0, [x for x in range(256)]))

    # print("Format zeros: ", format_zeros)

    syndromes = [[gf_pow(zero, 14 - m) for m in range(15)] for zero in format_zeros]
    b = []

    for row in syndromes:
        sum = 0
        for m in range(15):
            if format_mask[m]:
                sum = gf_add(row[m], sum)

        b.append(sum)

    return syndromes, b

# Also deals with the padding bits
def apply_format_information(ec_level, mask, matrix):

    GF = galois.GF(256)
    init_tables()

    A, b = apply_format_syndromes()

    # print(A)

    match ec_level:
        case "low":
            ec_bits = [1, 1]
        case "med":
            ec_bits = [1, 0]
        case "quart":
            ec_bits = [0, 1]
        case "high":
            ec_bits = [0, 0]

    mask_bits = [(mask ^ 0b101) // 4, (mask ^ 0b101) // 2 % 2, (mask ^ 0b101) % 2]

    first_five = ec_bits + mask_bits

    for i in range(5):
        A.append([0] * i + [1] + [0] * (14 - i))
        b.append(first_five[i])

    gf_A = GF(A)
    gf_b = GF(b)

    format = numpy.linalg.solve(gf_A, gf_b)

    for i in range(15):
        row, col = qr_coords_format(i)
        assert(format[i] == matrix[row][col])

    backup_format_strip = [(i, 8) for i in range(28, 21, -1)] + [(8, 8), (7,8)] + [(i, 8) for i in range(5, -1, -1)]
    
    global known_blacks, known_whites

    for i in range(15):
        if format[i]:
            known_blacks += [qr_coords_format(i), backup_format_strip[i]]
        else:
            known_whites += [qr_coords_format(i), backup_format_strip[i]]

    # Padding bits
    for point in [(i, 0) for i in range(17, 21)] + [(i, 1) for i in range (18, 21)]:
        if is_masked(point, mask):
            known_blacks.append(point)
        else:
            known_whites.append(point)



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

    # Calculate the directional sums
    sums = set_up_sums(matrix, size)

    # Apply the low-pass filter
    directions_removed = blur(sums, blur_level=blur_level)

    # Apply the format information and error correction reductions
    apply_format_information(ec, mask, matrix)

    # Apply the fixed structure reduction
    # reduce_data(sums, size)

    # Fixed stucuture and format reductions were correct
    assert reduced_structure_matches_original(matrix)


    # points_removed = len(known_blacks + known_whites)
    # print("Total points removed %d; points remaining: %d" % (points_removed, 29 * 29 - points_removed))
    

    # K = {"low" : 15, "med" : 26, "quart" : 36, "high" : 44}
    # k = K[ec]
    # n = 70 - k
    # A, b = gf_linear_system(sums, size, n, k, mask)
    
    # # print(A)
    # gf_A = GF(A)
    # gf_b = GF(b)

    # print("Rank of galois field systme: %d" % numpy.linalg.matrix_rank(gf_A))
    # print("Maximum rank expected: %d" % ((30 - directions_removed) * 29 + k))
    # print("Directional sums removed: %d; directional sums left: %d; expected direcitonal sums left: %d" % (directions_removed * 29, len(A) - k, 29 * (30 - directions_removed)))

    # test_gf_system(gf_A, gf_b, matrix)


    ### Alternating projections stuff
    # solution = alt_projection.solve(A, b)
    # actual_x = []
    # for row, col in coord_to_index_map.keys():
    #     actual_x.append(matrix[row][col])
    
    # solution = alt_projection.solve(A, b, actual_x)

    # assert(all([actual_x[i] == solution[i] for i in range(len(actual_x))]))

    # print("solution found")
    
    # exit()

    ### ILP solution
    solution = solve(sums.sumLibrary, sums.size, qr_code=False, add_constraints= True, print_solution=False)

    # Use a fold to flatten the boolean matrix
    matches = reduce(lambda x, y: x + y, [[solution[i][j] is None or int(solution[i][j]) == matrix[i][j] for i in range(size)] for j in range(size)], [])
    assert(all(matches))



if __name__ == "__main__":
    main()