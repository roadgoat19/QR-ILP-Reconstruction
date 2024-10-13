import pulp
from directionalsums import SumCalculator
#example sum library, n = 5
# import deblur
from constraints0123 import add_constraints0123
from constraints4567 import add_constraints4567


def write_dict_to_file(data_dict):
    with open('output.csv', 'w') as file:
        file.write("Point,Accuracy\n")
        for key, value in data_dict.items():
            file.write(f"{key},{value}\n")

#solve ilp given by sum_library (use directionalsums.py) of matrix size n
# known_pixels is a list of pixels coordinates whose values have already been removed from the sum_library with adjustDirectionalSums
def solve_ilp(sum_library, n, qr_code = True, add_constraints = False,p = 0, print_solution = True):
    #initialize problem
    problem = pulp.LpProblem("MatrixReconstruction", pulp.LpMinimize)

    #create dictionary of binary variables, each representing coordinates of the matrix
    variables = pulp.LpVariable.dicts("Cell", (range(n), range(n)), cat='Binary')

    #adds sum constraints
    for key, value in sum_library.items():
        cells, required_sum = value
        problem += pulp.lpSum(variables[row][col] for row, col in cells) == required_sum, f"SumConstraint_{key}"
    
    # factor in equivalence of both format strings
    if qr_code:
        # This is currently handled by deblur, since we are assuming masking and error correction level are known
        horz_strip, vert_strip = list(range(0, 6)) + [7] + list(range(n - 8, n)), list(range(n - 1, n - 8, -1)) + list(range(8, 6, -1)) + list(range(5, -1, -1))
        print(horz_strip)
        print(vert_strip)
        for horz, vert in zip(horz_strip, vert_strip):
            problem += pulp.lpSum([variables[8][horz], -1 * variables[vert][8]]) == 0, f"FormatConstraint_{horz}"

        if add_constraints:
            add_constraints0123(problem, variables)
            add_constraints4567(problem, variables)

    #only looking for feasible  solution at the moment, so objective is arbitrary
    # problem += variables[p[0]][p[1]], "ArbitraryObjective"
    # problem += variables[0][0], "Arbitrary Objective"


    #problem.writeLP(filename="test.lp", writeSOS=1, mip=1)

    # solve the problem
    problem.solve()

    # Check the status of the solution
    if pulp.LpStatus[problem.status] == 'Optimal':
        # Extract the solution
        solution_matrix = [[variables[i][j].varValue for j in range(n)] for i in range(n)]
        print("Solution found:")
        
        if print_solution:
            for row in solution_matrix:
                print(row)

        return solution_matrix
    else:
        print("No feasible solution found.")
        exit()

# Runs ILP with relaxed constraints to reflect removal of 22 bytes of message
def solve_relaxed_message(sum_library, n, print_solution = False):
    #initialize problem
    problem = pulp.LpProblem("MatrixReconstruction", pulp.LpMinimize)

    #create dictionary of binary variables, each representing coordinates of the matrix
    variables = pulp.LpVariable.dicts("Cell", (range(n), range(n)), cat='Binary')

    #adds sum constraints
    for key, value in sum_library.items():
        cells, (min, max) = value
        if min == max: # I don't know if this will ever happen
            problem += pulp.lpSum(variables[row][col] for row, col in cells) == max, f"SumConstraint_{key}"
        else: 
            problem += pulp.lpSum(variables[row][col] for row, col in cells) <= max, f"SumMax_{key}"
            problem += pulp.lpSum(variables[row][col] for row, col in cells) >= min, f"SumMin_{key}"

    # problem.setObjective(pulp.lpSum(variables.values()))

    problem.solve()

    # Check the status of the solution
    if pulp.LpStatus[problem.status] == 'Optimal':
        # Extract the solution
        solution_matrix = [[variables[i][j].varValue for j in range(n)] for i in range(n)]
        print("Solution found:")
        
        if print_solution:
            for row in solution_matrix:
                print(row)

        return solution_matrix
    else:
        print("No feasible solution found.")
        exit()
    

#runs linear programming with relaxed constrainst to find value of a key pixel
def solve_relaxed(point, sum_library, n, qr_code = True, add_constraints = False):
    problem = pulp.LpProblem("MatrixReconstruction", pulp.LpMaximize)

    #create dictionary of binary variables, each representing coordinates of the matrix
    variables = pulp.LpVariable.dicts("Cell", (range(n), range(n)), lowBound=0, upBound=1, cat='Continuous')

    #adds sum constraints
    for key, value in sum_library.items():
        cells, required_sum = value
        problem += pulp.lpSum(variables[row][col] for row, col in cells) == required_sum, f"SumConstraint_{key}"
    
    # factor in equivalence of both format strings
    if qr_code:
        horz_strip, vert_strip = list(range(0, 6)) + [7] + list(range(n - 8, n)), list(range(n - 1, n - 8, -1)) + list(range(8, 6, -1)) + list(range(5, -1, -1))
        print(horz_strip)
        print(vert_strip)
        for horz, vert in zip(horz_strip, vert_strip):
            problem += pulp.lpSum([variables[8][horz], -1 * variables[vert][8]]) == 0, f"FormatConstraint_{horz}"

        if add_constraints:
            add_constraints0123(problem, variables)
            add_constraints4567(problem, variables)

    #We maximize the value of the point and see if it can equal 1
    problem += variables[point[0]][point[1]], "Maximize point"


    problem.writeLP(filename="test.lp", writeSOS=1, mip=1)

    # solve the problem
    problem.solve()

    # Check the status of the solution
    # if pulp.LpStatus[problem.status] == 'Optimal':
    if True:
        # Extract the solution
        solution_matrix = [[variables[i][j].varValue for j in range(n)] for i in range(n)]
        print("Solution found for maximize:")
        for row in solution_matrix:
            print(row)
        print(variables[point[0]][point[1]].varValue)
        if variables[point[0]][point[1]].varValue != 1:
            print("Point must be 0.")
            return solution_matrix
    else:
        print("No feasible solution found.")

    print("No information gained, trying minimize.")

    problem = pulp.LpProblem("MatrixReconstruction", pulp.LpMinimize)

    #create dictionary of binary variables, each representing coordinates of the matrix
    variables = pulp.LpVariable.dicts("Cell", (range(n), range(n)), lowBound=0, upBound=1, cat='Continuous')

    #adds sum constraints
    for key, value in sum_library.items():
        cells, required_sum = value
        problem += pulp.lpSum(variables[row][col] for row, col in cells) == required_sum, f"SumConstraint_{key}"
    
    # factor in equivalence of both format strings
    if qr_code:
        horz_strip, vert_strip = list(range(0, 6)) + [7] + list(range(n - 8, n)), list(range(n - 1, n - 8, -1)) + list(range(8, 6, -1)) + list(range(5, -1, -1))
        print(horz_strip)
        print(vert_strip)
        for horz, vert in zip(horz_strip, vert_strip):
            problem += pulp.lpSum([variables[8][horz], -1 * variables[vert][8]]) == 0, f"FormatConstraint_{horz}"

        if add_constraints:
            add_constraints0123(problem, variables)
            add_constraints4567(problem, variables)

    #We minimize the value of the point and see if it can equal 0
    problem += variables[point[0]][point[1]], "Minimize point"


    #problem.writeLP(filename="test.lp", writeSOS=1, mip=1)

    # solve the problem
    problem.solve()

    # Check the status of the solution
    # if pulp.LpStatus[problem.status] == 'Optimal':

    if True:
        # Extract the solution
        solution_matrix = [[variables[i][j].varValue for j in range(n)] for i in range(n)]
        print("Solution found for maximize:")
        for row in solution_matrix:
            print(row)
        print(variables[point[0]][point[1]].varValue)
        if variables[point[0]][point[1]].varValue != 0:
            print("Point must be 1.")
            return solution_matrix
    else:
        print("No feasible solution found.")

    print("No information gained.")



def check_solution(Correct, Guess):
    # Iterate through each element and compare
    for i in range(len(Correct)):
        for j in range(len(Correct[0])):
            if Correct[i][j] != Guess[i][j]:
                return False
                
    # If all elements match, the arrays are identical
    return True

def sum_matrix(Correct, guess):
    sum = 0
    for i in range(len(Correct)):
        for j in range(len(Correct[0])):
            if Correct[i][j] == guess[i][j] or guess[i][j] == None:
                sum += 1
    return sum / (29*29)

def accuracy_matrix(correct, guess):
    solution_matrix = [[guess[i][j] == correct[i][j] or guess[i][j] == None for j in range(29)] for i in range(29)]
    for x in solution_matrix:
        for i in range(len(x)):
            if x[i] == True:
                x[i] = 1
            else:
                x[i] = 0
        
    for row in solution_matrix:
        print(row)

# def main():
#     n = int(input("Enter the size of the matrix (N x N): "))

#     sum_calc = SumCalculator(n)
#     sum_calc.printMatrix()
#     sum_calc.computeAllDirectionalSums()


#     sum_calc.removeDirectionalSums(6)
#     sum_calc.removeDirectionalSums(5)
#     sum_calc.removeDirectionalSums(4)
#     sum_calc.removeDirectionalSums(3)
#     sum_calc.removeDirectionalSums(2)

#     #deblur.reduce_data(sum_calc, 29)

#     print("Removing directional sums: ")

#     Accuracies = {}

#     #in this example, it computes the correct matrix
#     for i in range(29):
#         for j in range(29):
#             guess = solve_ilp(sum_calc.sumLibrary, sum_calc.size, qr_code=True, p=(i,j) )
#             correct = sum_calc.matrix
#             Accuracies[(i,j)] = sum_matrix(correct, guess)
#     maxKey = max(Accuracies, key=lambda key: Accuracies[key])
#     minKey = min(Accuracies, key=lambda key: Accuracies[key])
#     print(f"Maximum: {maxKey}: {Accuracies[maxKey]}")
#     print(f"Minimum: {minKey}: {Accuracies[minKey]}")
#     write_dict_to_file(Accuracies)
#     #print(check_solution(correct, guess))
#     #accuracy_matrix(correct, guess)

#     # solve_relaxed([8,2], sum_calc.sumLibrary, sum_calc.size, qr_code=True, add_constraints=True)
#     # print("Point really was: " + str(sum_calc.matrix[8][2]))





def main():
    # n = int(input("Enter the size of the matrix (N x N): "))
    n = 29

    sum_calc = SumCalculator(n)
    sum_calc.printMatrix()
    sum_calc.computeAllDirectionalSums()
    sum_calc.printDirectionalSums()

    #in this example, it computes the correct matrix
    actual = solve_ilp(sum_calc.sumLibrary, sum_calc.size, qr_code=False)
    assert(check_solution(sum_calc.matrix, actual))





if __name__ == "__main__":
    main()