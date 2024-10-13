import random
from solution_space import solution_space
from reedsolo import *
import numpy as np
import galois

# Returns the matrix for orthogonal projection onto the solution space of Ax = b
def orth_proj_map(A, b):
    
    shift, null_space = solution_space(A, b)

    print("null_space dimension is %d, and null_space matrix has %d columns" % (np.linalg.matrix_rank(null_space), len(null_space[0])))

    null_transpose = null_space.transpose()

    BTB = np.matmul(null_transpose, null_space)
    BTB_inv = np.linalg.inv(BTB)

    proj = np.matmul(null_space, np.matmul(BTB_inv, null_transpose))

    return proj, shift

def project_on_1(proj, shift, x):
    
    GF = galois.GF(256)

    gf_x = GF(x)

    shifted = np.subtract(gf_x, shift)

    projected = np.matmul(proj, shifted)
    
    reshifted = np.add(projected, shift)

    return reshifted

def project_on_2(x):
    
    projected = []

    for set in range(70):
        sum = 0
        for i in range(8):
            sum = gf_add(sum, gf_mul(gf_pow(2, 7 - i), x[i + set * 8]))

        assert sum < 256

        for _ in range(8):
            projected.append((sum >> 7) & 1)
            sum = sum << 1
    
    # print(projected)
    return projected


def solve(A, b, input):
    
    proj, shift = orth_proj_map(A, b)

    # oldx = [random.randint(0,1) for _ in A[0]]
    oldx = input
    oldx[0] = 1 if oldx[0] == 0 else 0
    # for i in range(10):
    #     oldx[i] = not oldx[i]
    x = project_on_1(proj, shift, oldx)

    while any(x_elt != old_elt for x_elt, old_elt in zip(x, oldx)):
        oldx = project_on_2(x)
        # exit()
        x = project_on_1(proj, shift, oldx)
        print("difference between: %d" % sum(x_elt != old_elt for x_elt, old_elt in zip(x, oldx)))
        print("difference x from input: %d" % sum(x_elt != input_elt for x_elt, input_elt in zip(x, input)))
        print("difference oldx from input: %d" % sum(input_elt != old_elt for input_elt, old_elt in zip(input, oldx)))

        # exit()

    return(x)

    