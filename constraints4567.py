import pulp 

def add_constraints4567(problem, variables):

    x1 = variables[17][0]
    x2 = variables[18][0]
    x3 = variables[19][0]
    x4 = variables[20][0]
    x5 = variables[18][1]
    x6 = variables[19][1]
    x7 = variables[20][1]
    
    y1 = variables[8][2]
    y2 = variables[8][3]
    y3 = variables[8][4]

    z1 = variables[27][27]
    z2 = variables[28][27]
    z3 = variables[27][28]
    z4 = variables[28][28]
    

    m4 = pulp.LpVariable("m4", cat = "Binary")
    m5 = pulp.LpVariable("m5", cat = "Binary")
    m6 = pulp.LpVariable("m6", cat = "Binary")
    m7 = pulp.LpVariable("m7", cat = "Binary")

    p4 = pulp.LpVariable("p4",cat = "Binary")
    p5 = pulp.LpVariable("p5",cat = "Binary")
    p6 = pulp.LpVariable("p6",cat = "Binary")
    p7 = pulp.LpVariable("p7",cat = "Binary")

    e4 = pulp.LpVariable("e4", cat = "Binary")
    e5 = pulp.LpVariable("e5", cat = "Binary")
    e6 = pulp.LpVariable("e6", cat = "Binary")
    e7 = pulp.LpVariable("e7", cat = "Binary")

    # Mask 4

    # Mask bits 
    problem += -y1 - y2 +y3 - 3 * m4 <= 0
    problem += -y1 - y2 +y3 - 3 * m4 >= -2

    # Padding bits
    problem += x1 - x2 - x3 + x4 - x5 - x6 + x7 - 7 * p4 <= 2
    problem += x1 - x2 - x3 + x4 - x5 - x6 + x7 - 7 * p4 >= -4

    # Mask implies Padding
    problem += m4 <= p4

    # Encoding 
    problem += z1 + z2 + z3 - z4 - 4 * m4 <= 2
    problem += z1 + z2 + z3 - z4 - 4 * m4 >= -1

    # Mask implies Encoding

    # Mask iff subset of padding
    problem += x2 + m4 == 1


    # Mask 5

    # Mask bits 
    problem += -y1 - y2 -y3 - 3 * m5 <= -1
    problem += -y1 - y2 -y3 - 3 * m5 >= -3

    # Padding bits
    problem += x1 + x2 + x3 + x4 + x5 - x6 - x7 - 7 * p5 <= 4
    problem += x1 + x2 + x3 + x4 + x5 - x6 - x7 - 7 * p5 >= -2

    # Mask implies Padding
    problem += m5 <= p5

    # Encoding 
    problem += - z1 - z2 + z3 - z4 - 4 * e5 <= 0
    problem += - z1 - z2 + z3 - z4 - 4 * e5 >= -3

    # Mask implies Encoding
    problem += m5 <= e5

    # Mask iff subset of padding
    problem += x5 - x7 - 2 * m5 <= 0
    problem += x5 - x7 - 2 * m5 >= -1

    
    # Mask 6

    # Mask bits 
    problem += -y1 + y2 +y3 - 3 * m6 <= 1
    problem += -y1 + y2 +y3 - 3 * m6 >= -1

    # Padding bits
    problem += x1 + x2 + x3 + x4 + x5 + x6 + x7 - 7 * p6 <= 6
    problem += x1 + x2 + x3 + x4 + x5 + x6 + x7 - 7 * p6 >= 0

    # Mask implies Padding
    problem += m6 <= p6

    # Encoding 
    problem += - z1 - z2 + z3 - z4 - 4 * e6 <= 0
    problem += - z1 - z2 + z3 - z4 - 4 * e6 >= -3

    # Mask implies Encoding
    problem += m6 <= e6

    # Mask iff subset of padding
    problem += x5 + x6 - 2 * m6 <= 1
    problem += x5 + x6 - 2 * m6 >= 0

    
    # Mask 7

    # Mask bits 
    problem += -y1 + y2 -y3 - 3 * m7 <= 0
    problem += -y1 + y2 -y3 - 3 * m7 >= -2

    # Padding bits
    problem += - x1 + x2 - x3 + x4 - x5 - x6 - x7 - 7 * p7 <= 1
    problem += - x1 + x2 - x3 + x4 - x5 - x6 - x7 - 7 * p7 >= -5

    # Mask implies Padding
    problem += m7 <= p7

    # Encoding 
    problem += z1 + z2 - z3 - z4 - 4 * e7 <= 1
    problem += z1 + z2 - z3 - z4 - 4 * e7 >= -2

    # Mask implies Encoding
    problem += m7 <= e7

    # Mask iff subset of padding
    problem += -x3 - x6 - x7 - 3 * m7 <= -1
    problem += -x3 - x6 - x7 - 3 * m7 >= -3