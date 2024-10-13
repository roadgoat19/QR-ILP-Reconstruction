from deblur import *
import operator
import random

def rand_comb(N, K):
    comb = set()
    for j in range(N - K, N):
        t = random.randint(0, j - 1)
        if t not in comb:
            comb.add(t)
        else:
            comb.add(j)
    return comb

# Code from https://stackoverflow.com/questions/66192894/precise-determinant-of-integer-nxn-matrix
def int_det(M):
    M = [row[:] for row in M] # make a copy to keep original M unmodified
    N, sign, prev = len(M), 1, 1
    for i in range(N-1):
        if M[i][i] == 0: # swap with another row having nonzero i's elem
            swapto = next( (j for j in range(i+1,N) if M[j][i] != 0), None )
            if swapto is None:
                return 0 # all M[*][i] are zero => zero determinant
            M[i], M[swapto], sign = M[swapto], M[i], -sign
        for j in range(i+1,N):
            for k in range(i+1,N):
                assert ( M[j][k] * M[i][i] - M[j][i] * M[i][k] ) % prev == 0
                M[j][k] = ( M[j][k] * M[i][i] - M[j][i] * M[i][k] ) // prev
        prev = M[i][i]
    return sign * M[-1][-1]


def main():
    global known_blacks, known_whites
    GF = galois.GF(256)
    init_tables()

    input = "./codes/low0.txt" # Note that the qr code actually doesn't matter for these tests
    blur_level = 5

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
    reduce_data(sums, size)

    # Fixed stucuture and format reductions were correct
    assert reduced_structure_matches_original(matrix)


    points_removed = len(known_blacks + known_whites)
    print("Total points removed %d; points remaining: %d" % (points_removed, 29 * 29 - points_removed))
    

    K = {"low" : 15, "med" : 26, "quart" : 36, "high" : 44}
    k = K[ec]
    n = 70 - k
    A, _ = gf_linear_system(sums, size, n, k, mask, include_ec = False)

    full = A + [[int(i == j) for i in range(560)] for j in range(560)]

    # A = numpy.mat(full)
    A = full

    m = len(full)
    n = len(full[0])
    print("Dimensions of A: %d x %d" % (m, n))

    for i in range(m):
        if A[i][551] == 1:
            print(i)
    
    ## For blur level 5,
    # 13, 30, 75, 101, 667 have a 1 in column 551
    # 13, 29, 74, 100, 668 have a 1 in column 552
    # 14, 30, 74, 102, 669 have a 1 in column 553
    # 14, 29, 73, 101, 670 have a 1 in column 554
    # 15, 30, 73, 103, 671 have a 1 in column 556
    # 15, 29, 72, 102, 672 have a 1 in column 557
    # 16, 30, 72, 104, 673 have a 1 in column 558
    # 16, 29, 71, 103, 674 have a 1 in column 559
    # 17, 30, 71, 105, 675 have a 1 in column 560
    
    # exit()
    dets = set()

    # subs = list(itertools.combinations(range(m), n))

    subs = [
        list(range(560)), # First 560 rows of A
        list(range(m - n, m)), # Last 560 rows of A (identity)
        list(range(m - n, m - 1)) + [17], # Identity with last row replaced by a directional sum that has a one in the last column
        list(range(m - n, m - 2)) + [17, 16],
        list(range(m - n, m - 3)) + [17, 16, 30],
        list(range(m - n, m - 4)) + [17, 16, 30, 15],
        list(range(m - n, m - 5)) + [17, 16, 30, 15, 73],
        list(range(m - n, m - 6)) + [17, 16, 30, 15, 73, 29],
        list(range(m - n, m - 7)) + [17, 16, 30, 15, 73, 29, 74],
        list(range(m - n, m - 8)) + [17, 16, 30, 15, 73, 29, 74, 13],
        list(range(m - n, m - 9)) + [17, 16, 30, 15, 73, 29, 74, 13, 101] # Couldn't get a nonzero here by changing the last row
    ]

    print("Selected Determinants: ")

    for i in range(len(subs)):

        mat = [A[j] for j in subs[i]]

        print("\tdet%d = %2d" % (i, numpy.linalg.det(mat)))

    # exit()

    # Hadamard's inequality gives a bound on all of the subdeterminants:
    # Need columns of A:

    transpose = [[A[j][i] for j in range(m)] for i in range(n)]
    
    norm_sq = lambda lst: sum([elt ** 2 for elt in lst])
    col_norm_sq = list(map(norm_sq, transpose))

    # print(col_norm_sq)

    bound = numpy.sqrt(numpy.prod(col_norm_sq))

    print("Hadamard bound is %d, although overflow was likely" % bound)

    subs = itertools.combinations(range(m), n)

    N_ITERATIONS = 10000

    # for subset in subs:

    #     # mat = operator.itemgetter(*full)(subset)
    #     # mat = numpy.asarray(A)[subset].tolist()
    #     # print(subset)

    #     mat = [A[i] for i in subset]

    #     # # Wanted to see if computing rank was faster
    #     # rank = numpy.linalg.matrix_rank(mat)
    #     # dets.append(0 if rank < 560 else numpy.linalg.det(mat))

    #     dets.append(numpy.linalg.det(mat))

    #     if len(dets) % 100 == 0:
    #         print("%d" % len(dets))

    #     if (len(dets) == N_ITERATIONS):
    #         break

    nonzeros = []

    random.seed(0)

    for i in range(N_ITERATIONS):

        subset = rand_comb(m, n)

        mat = [A[i] for i in subset]

        det = numpy.linalg.det(mat)
        # det = int(numpy.linalg.det(mat))
        dets.add(det) # Not sure if int cast can make the answer wrong...
        if det != 0:
            nonzeros.append(subset)
        # dets.append(int_det(mat)) Extremely slow

        if i % 100 == 0:
            print("Iterations completed: %d" % i)

    # print("Number of 0's: %d in first %d iterations" % (len(list(filter(lambda x: x == 0, dets))), N_ITERATIONS)) all 0's in 100000 iterations
    zeros = N_ITERATIONS - len(dets) + 1 # Assumes we found atleast 1 determinant 0
    print("Number of 0's: %d in %d random iterations" % (zeros, N_ITERATIONS))

    print("Determinants: ", set(dets))

    dets = set()
    for subset in nonzeros:
        
        mat = [A[i] for i in subset]
        int_det_val = int_det(mat)
        dets.add(int_det_val)
        if int_det_val == 0:
            zeros += 1
        print("numpy: %10d; integer: %10d\t%s" %  (numpy.linalg.det(mat), int_det_val, str(list(subset).sort())[:39]))


    print("Number of 0's: %d in %d random iterations" % (zeros, N_ITERATIONS))
    print("Determinants: ", set(dets))



    # print(len(subs))



if __name__ == "__main__":
    main()