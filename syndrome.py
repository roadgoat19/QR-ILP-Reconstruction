from reedsolo import *

n = 5
k = 10

rs = RSCodec(nsym=k)
init_tables()

# EC Low (01), mask 0
message = [0, 1, 0, 0, 0]

XOR_with = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
expected = 	[1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0]

# encoded = rs_encode_msg(message, nsym= n) # for some reason this is different
encoded = rs.encode(message)
_, remainder = gf_poly_div(message + 10 * [0], [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1])
encoded_message = [x ^ y for (x, y) in zip((message + list(remainder)), XOR_with)]



syndromes = rs_calc_syndromes(msg= encoded_message, nsym= k)

print("Syndromes: ")

print(syndromes)

print("Encoded message: ")

for i in range(n + k):
    print("Expected: %d, actual: %d" % (expected[i], encoded_message[i]))

syndromes = [gf_poly_eval(encoded_message, gf_pow(2, j)) for j in range(k)]

print(syndromes)


# #print error correction bytes in decimal and binary and ASCII representation
# for i in range(k):
#     print("Error Correction Byte", i, ":", encoded[-k + i], "(", format(encoded[-k + i], "08b"), ")", "(", chr(encoded[-k + i]), ")")

# tamper(encoded)

#print(encoded)

# syndromes = rs_calc_syndromes(msg= encoded, nsym= k)

# print("Tampered Syndromes: ")

# print(syndromes)

# def pow(x, power):
#     return x ** power

# def poly_eval(poly, x):
#     y = poly[0]
#     for i in xrange(1, len(poly)):
#         y = (y * x + poly[i])
#     return y

# def calc_syndromes(msg, nsym = k, fcr=0, generator=2):
#     return [0] + [poly_eval(msg, pow(generator, i+fcr)) for i in xrange(nsym)]

# syndromes = calc_syndromes(encoded)

# print("Syndromes: (Non Galois)")

# print(syndromes)

# print("Syndromes mod 256:")

# print([x % 256 for x in syndromes])

# # Notes: 
# # syndromes were 1 sometimes when the length of the message less than or equal to n
# # if we compute the syndromes as a regular polynomial, they are huge (overflow)

# # Questions:
# # Why can they use mod 255 in exponentiation?



format_generator = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]

for x in range(256):
    if gf_poly_eval(format_generator, x) == 0:
        print("%d is a zero of the format generator" % x)

format_zeros = [10, 68, 78, 79, 146, 152, 153, 214, 215, 221]

assert format_zeros == list(filter(lambda x: gf_poly_eval(format_generator, x) == 0, [x for x in range(256)]))

L0_format = [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0]

L1_format = [1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1]

Q6_format = [0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0]

print("format zeros:")
for x in format_zeros:
    print(gf_poly_eval(L0_format, x), gf_poly_eval(L1_format, x), gf_poly_eval(Q6_format, x))

print("format zeros (before the XOR step):")

L0_format_pre_XOR = [x ^ y for (x, y) in zip(L0_format, XOR_with)]
L1_format_pre_XOR = [x ^ y for (x, y) in zip(L1_format, XOR_with)]
Q6_format_pre_XOR = [x ^ y for (x, y) in zip(Q6_format, XOR_with)]

for x in format_zeros:
    print(gf_poly_eval(L0_format_pre_XOR, x), gf_poly_eval(L1_format_pre_XOR, x), gf_poly_eval(Q6_format_pre_XOR, x))

print("other values:")
for x in [0, 1, 2, 7]:
    print(gf_poly_eval(L0_format, x), gf_poly_eval(L1_format, x), gf_poly_eval(Q6_format, x))

A = [[gf_pow(zero, 14 - m) for m in range(15)] for zero in format_zeros]

# Augment the matrix:

for row in A:
    sum = 0
    for m in range(15):
        if XOR_with[m]:
            sum = gf_add(row[m], sum)

    row.append(sum)

import numpy

print(numpy.array(A))

print("And we get the same format zeros as the augmented column!")