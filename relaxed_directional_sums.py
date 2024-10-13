import random
import numpy as np

class SumCalculator:

    def __init__(self, size, matrix = None):
        self.size = size
        self.matrix = [[random.randint(0,1) for _ in range(size)] for _ in range(size)] if matrix is None else matrix
        
        self.sumLibrary = {}
        self.directionalSumMatrix = []

    # We have p+1 distinct directional sums
    # - p lines per distinct sum
    #Returns points in the line and sum of given start index and slope
    def slopeSum(self,start,slope):
        n = self.size
        line = []
        row, column = start[0],start[1]
        rise, run = slope[0],slope[1]
        rowSum = 0
        rowSum += self.matrix[row][column]
        line.append((row,column))
        for i in range(n-1):
            newRow = abs(row+rise) % n
            newColumn = abs(column+run) % n
            rowSum += self.matrix[newRow][newColumn]
            line.append((newRow,newColumn))
            row = row+rise
            column = column+run
        return [line,rowSum]
    #All other slope sums
    def otherSums(self):
        n = self.size
        for i in range(n):
            slope = (1,i)
            for j in range(n):
                start = (0,j)
                line, sum = self.slopeSum(start,slope)
                self.sumLibrary[(start,slope)] = line, (sum, sum)
    #Row and Column Sums
    def rowSums(self):
        n = self.size
        for i in range(n):
            start = (i,0)
            slope = (0,1)
            line, sum = self.slopeSum(start,slope)
            self.sumLibrary[(start,slope)] = line, (sum, sum)

    def columnSums(self):
        for i in range(self.size):
            start = (0,i)
            slope = (1,0)
            line, sum = self.slopeSum(start,slope)
            self.sumLibrary[(start,slope)] = line, (sum, sum)
    #Calls directional sum functions to update sumLibrary
    def computeAllDirectionalSums(self):
        self.rowSums()
        self.columnSums()
        self.otherSums()

    def printDirectionalSums(self):
        n = self.size
        count = 0
        for key, value in self.sumLibrary.items():
                start, slope = key
                line, rowSum = value
                if count == 0:
                    print("Row sums:")
                if count == n:
                    print("Column sums: ")
                if count == 2 * n:
                    print("Other sums: ")
                print(f"Start: {start}, Slope: {slope}, Line: {line}, Sum: {rowSum}")
                count +=1
    #Removes 1 from directional sums containing a point
    def adjustDirectionalSums(self,knownPoint,val):
    #val = matrix[knownPoint[0]][knownPoint[1]]
        for key, value in self.sumLibrary.items():
            points = value[0]
            sum_min, sum_max = value[1]
            for point in points:
                if point[0] == knownPoint[0] and point[1] == knownPoint[1]:
                    newPoints = [point for point in points if point != knownPoint]
                    self.sumLibrary[key] = [newPoints, (sum_min - val, sum_max - val)]

    def relaxDirectionalSums(self, knownPoint):
        for key, value in self.sumLibrary.items():
            points = value[0]
            sum_min, sum_max = value[1]
            for point in points:
                if point[0] == knownPoint[0] and point[1] == knownPoint[1]:
                    newPoints = [point for point in points if point != knownPoint]
                    self.sumLibrary[key] = [newPoints, (sum_min - 1, sum_max)]


    def removeDirectionalSums(self, n):
        levels = [[(1, 29), (29,1), (1, 1), (1, 28)],
                  [(1,2), (1,27), (1, 15), (1, 14)],
                  [(1,19),  (1,10)],
                  [(1, 3), (1, 26), (1,16), (1,13), (1, 20), (1, 9)],
                  [(1,4), (1,25), (1, 8), (1, 21), (1, 22), (1,7), (1,11), (1,18)],
                  [(1,5), (1,24), (1,23), (1,6), (1,12),(1,17)]]
        
        print(n)
        # slopes = levels[n-1]
        slopes = levels[n]

        for slope in slopes:
            for j in range(self.size):
                del self.sumLibrary[((0,j), slope)]

        return len(slopes)
    
    def updateDirectionalSumMatrix(self):
        self.directionalSumMatrix = []
        for directionalSum in self.sumLibrary.values():
            points = directionalSum[0]
            sumList = [0 for _ in range(self.size*self.size)]
            for point in points:
                index = point[0]*self.size + point[1]
                sumList[index] = 1
            self.directionalSumMatrix.append(sumList)

    def printMatrix(self):
        print("The Matrix is: ")
        for row in self.matrix:
            print(' '.join(map(str, row)))    
    
    def printDirectionalSumMatrix(self):
        print("The Directional Sum Matrix is: ")
        for row in self.directionalSumMatrix:
            print(' '.join(map(str, row)))
    
    
def main():

    n = int(input("Enter the size of the matrix (N x N): "))

    sum_calc = SumCalculator(n)
    sum_calc.printMatrix()
    sum_calc.computeAllDirectionalSums()
    sum_calc.updateDirectionalSumMatrix()
    sum_calc.printDirectionalSumMatrix()

    sum_calc.removeDirectionalSums(5)
    sum_calc.updateDirectionalSumMatrix()
    #sum_calc.printDirectionalSums()

    #x = int(input("Input the x coordinate of the known point: "))
    #y = int(input("Input the y coordinate of the known point: "))
    #point = (x,y)
    matrixA = np.array(sum_calc.directionalSumMatrix)
    print("Rank: ",np.linalg.matrix_rank(matrixA))
    #sum_calc.adjustDirectionalSums(point, sum_calc.matrix[x][y])
    #sum_calc.printDirectionalSums()

if __name__ == "__main__":
    main()


