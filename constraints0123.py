import pulp

def add_constraints0123(problem, variables):
    y1, y2, y3 = variables[8][2], variables[8][3], variables[8][4]
    x1, x2, x3, x4, x5, x6, x7 = variables[17][0], variables[18][0], variables[19][0], variables[20][0], variables[18][1], variables[19][1], variables[20][1]
    z1, z2, z3, z4 = variables[27][27], variables[28][27], variables[27][28], variables[28][28]

    # Mask 0:
    m0 = pulp.LpVariable("m0", cat = "Binary")
    e0 = pulp.LpVariable("e0", cat = "Binary")
    p0 = pulp.LpVariable("p0", cat = "Binary")
    problem += pulp.lpSum([y1,-1 * y2, y3, -3 * m0]) <= 1
    problem += pulp.lpSum([y1,-1 * y2, y3, -3 * m0]) >= -1
    problem += pulp.lpSum([-1 * x1, x2,-1 * x3, x4, -1 * x5, x6, -1 * x7, -7 * p0]) <= 2
    problem += pulp.lpSum([-1 * x1, x2,-1 * x3, x4, -1 * x5, x6, -1 * x7, -7 * p0]) >= -4
    problem += pulp.lpSum([z1, z2, -1 * z3, z4, -4 * e0]) <= 2
    problem += pulp.lpSum([z1, z2, -1 * z3, z4, -4 * e0]) >= -1
    problem += m0 <= p0
    problem += m0 <= e0
    problem += pulp.lpSum([-1 * x3, x6, -2 * m0]) <= 0
    problem += pulp.lpSum([-1 * x3, x6, -2 * m0]) >= -1

    # Mask 1:
    m1 = pulp.LpVariable("m1", cat = "Binary")
    # e1 = pulp.LpVariable("e1", cat = "Binary")
    p1 = pulp.LpVariable("p1", cat = "Binary")
    problem += y1 - y2 - y3 - 3 * m1 <= 0
    problem += y1 - y2 - y3 - 3 * m1 >= -2
    problem += - x1 + x2 - x3 + x4 + x5 - x6 + x7 - 7 * p1 <= 3
    problem += - x1 + x2 - x3 + x4 + x5 - x6 + x7 - 7 * p1 >= -3
    problem += - z1 - z2 - z3 + z4 - 4 * m1 <= 0
    problem += - z1 - z2 - z3 + z4 - 4 * m1 >= -3
    problem += - x1 + x5 - 2 * m1 <= 0
    problem += - x1 + x5 - 2 * m1 >= -1

    # Mask 2:
    m2 = pulp.LpVariable("m2", cat = "Binary")
    e2 = pulp.LpVariable("e2", cat = "Binary")
    p2 = pulp.LpVariable("p2", cat = "Binary")
    problem += y1 + y2 + y3 - 3 * m2 <= 2
    problem += y1 + y2 + y3 - 3 * m2 >= 0
    problem += x1 + x2 + x3 + x4 - x5 - x6 - x7 - 7 * p2 <= 3
    problem += x1 + x2 + x3 + x4 - x5 - x6 - x7 - 7 * p2 >= -3
    problem += m2 <= p2
    problem += z1 - z2 - z3 - z4 - 4 * m2 <= 0
    problem += z1 - z2 - z3 - z4 - 4 * m2 >= -3
    problem += x3 - x5 - x6 - 3 * m2 <= 0
    problem += x3 - x5 - x6 - 3 * m2 >= -2

    # Mask 3:
    m3 = pulp.LpVariable("m3", cat = "Binary")
    e3 = pulp.LpVariable("e3", cat = "Binary")
    p3 = pulp.LpVariable("p3", cat = "Binary")
    problem += y1 + y2 - y3 - 3 * m3 <= 1
    problem += y1 + y2 - y3 - 3 * m3 >= -5
    problem += m3 <= p3
    problem += - x1 + x2 - x3 - x4 - x5 - x6 + x7 - 7 * p3 <= 1
    problem += - x1 + x2 - x3 - x4 - x5 - x6 + x7 - 7 * p3 >= -5
    problem += z1 + z2 - z3 - z4 - 4 * e3 <= 1
    problem += z1 + z2 - z3 - z4 - 4 * e3 >= -2
    problem += m3 <= e3
    problem += x4 + m3 == 1