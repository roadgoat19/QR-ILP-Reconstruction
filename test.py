from reedsolo import *

# # Number of error correction bytes
# n = 7

# # Create a Reed-Solomon encoder/decoder
# rs = RSCodec(n)

# # Your message (in bytes)
# message = b"www.wikipedia.org"

# # Encode the message, which adds n error correction bytes at the end
# encoded_message = rs.encode(message)

# print("Encoded Message with Error Correction Bytes:", encoded_message)

# #print error correction bytes in decimal and binary and ASCII representation
# for i in range(n):
#     print("Error Correction Byte", i, ":", encoded_message[-n + i], "(", format(encoded_message[-n + i], "08b"), ")", "(", chr(encoded_message[-n + i]), ")")

# encoded_message[0] = 0
# print(encoded_message)
# decoded_message = rs.decode(encoded_message)
# print("Decoded Message:", decoded_message)



# for x in rs_generator_poly(7):
#     print("%d" % x)
    

# message = bytes([65, 23, 119, 119, 114, 231, 118, 150, 182, 151, 6, 86, 70, 150, 18, 230, 247, 38, 112])

# message_with_0s = bytes([65, 23, 119, 119, 114, 231, 118, 150, 182, 151, 6, 86, 70, 150, 18, 230, 247, 38, 112, 0, 0, 0, 0, 0, 0, 0])

# #print("Error correction bytes:")

# encoded_message = rs.encode(message)

# # expected error bytes
# expected = bytes([174, 173, 239, 6, 151, 143, 37])

# print("Encoded Message Error Correction Bytes:")

# #print error correction bytes in decimal and binary and ASCII representation
# for i in range(n):
#     print("Error Correction Byte %d: actual: %3d ( %c ) | expected: %3d ( %c )" % (i, encoded_message[i+len(message)], encoded_message[i+len(message)], expected[i], expected[i]))

# print("Error correction bytes from polynomial division")

# _, remainder = gf_poly_div(message_with_0s, rs_generator_poly(7))

# for i in range(n):
#     print("Error Correction Byte %d: actual: %3d ( %c ) | expected: %3d ( %c )" % (i, remainder[i], remainder[i], expected[i], expected[i]))


# print(rs_calc_syndromes(encoded_message, n))


# encoded_message[5] = 0

# print(rs_calc_syndromes(encoded_message, n))

import numpy
import galois

# matrix = [[1, 0, 0, 1, 0, 0, 1, 0, 0],
#           [0, 1, 0, 0, 1, 0, 0, 1, 0],
#           [0, 0, 1, 0, 0, 1, 0, 0, 1],
#           [0, 1, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 1, 1, 0, 0, 0, 1, 0],
#           [1, 0, 0, 0, 1, 0, 0, 0, 1],
#           [0, 0, 1, 0, 1, 0, 1, 0, 0],
#           [1, 0, 0, 0, 0, 1, 0, 1, 0],
#           [0, 1, 0, 1, 0, 0, 0, 0, 1],
#           [0, 0, 0, 0, 0, 0, 1, 1, 1],
#           [0, 0, 0, 1, 1, 1, 0, 0, 0],
#           [1, 1, 1, 0, 0, 0, 0, 0, 0]]

# vector = [2, 2, 0, 2, 0, 2, 2, 1, 1, 1, 1, 2]

# augmented = matrix

# [augmented[i].append(vector[i]) for i in range(12)]

# print("augmented:")
# print(numpy.matrix(augmented))

# FF = galois.GF(5)

# FF_mat = FF(augmented)

# reduced = FF_mat.row_reduce()

# print("reduced")
# print(reduced)

# solutions = [int(reduced[i][9]) for i in range(12)]

# print("solutions")
# print(solutions)

# import sympy

# m = sympy.Matrix(augmented)

# m_rref = numpy.matrix(m.rref()[0])

# print(m_rref)

# solutions = [int(m_rref[i][9]) for i in range(12)]

# print(solutions)

# from random import randint

# x = [randint(0, 1) for _ in range(10)]

# GF = galois.GF(2 ** 8)

# print(x)
# gf_x = GF(x)
# print(GF(gf_x))



# test = list(range(13))

# rs = RSCodec(22)

# encoded = rs.encode(test)

# encoded[0] = 1

# decoded = rs.decode(encoded)

# print(decoded)

# exit()


import pulp as pl
solver_list = pl.listSolvers()
print(solver_list)

exit()





from deblur import *

init_tables()

# input = "./codes/high0.txt"
input = "./codes/low0.txt"
blur_level = 0

size, matrix = read_QR(input)

mask = get_mask(matrix)
ec = get_ec(matrix)
print("Mask: %d; EC Level: %s" % (mask, ec))

# rs = RSCodec(22)
rs = RSCodec(15)

block_message = []
    
for block_index in range(70):

    byte = 0

    for byte_index in range(8):

        byte = byte << 1

        message_index = block_index * 8 + byte_index
        print(message_index)
        row, col = qr_coords_message(message_index)

        byte += 0 if matrix[row][col] is None else int(matrix[row][col])


    # print(byte)
    
    block_message.append(byte)

tampered = [elt for elt in block_message]
tampered[0] = 1 if tampered[0] == 0 else 0
tampered[1] = 1 if tampered[1] == 0 else 0
print(tampered)
print(block_message)

decoded = rs.decode(tampered)

assert all([decoded[i] == block_message[i] for i in range(len(decoded))])

exit()


for block in range(1, 3):

    block_message = []
    
    for block_index in range(35):

        byte = 0

        for byte_index in range(8):

            byte = byte << 1

            message_index = (2 * block_index + block - 1) * 8 + byte_index
            print(message_index)
            row, col = qr_coords_message(message_index)

            byte += 0 if matrix[row][col] is None else int(matrix[row][col])


        # print(byte)
        
        block_message.append(byte)

    tampered = [elt for elt in block_message]
    tampered[0] = 1 if tampered[0] == 0 else 0
    tampered[1] = 1 if tampered[1] == 0 else 0
    print(tampered)
    print(block_message)

    decoded = rs.decode(block_message)

    assert all([decoded[i] == block_message[i] for i in range(len(decoded))])