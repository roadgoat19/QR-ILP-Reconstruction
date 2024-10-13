# Code from https://dev.to/maxart2501/let-s-develop-a-qr-code-generator-part-iv-placing-bits-3mn1

def fillArea(matrix, row, column, width, height, fill = 1):
    for i in range(row, row + height):
        for j in range(column, column + width):
            matrix[i][j] = fill

def getVersion(size):
    return (size - 17) // 4

def getModuleSequence(size):

    matrix = [[0 for _ in range(size)] for _ in range(size)]
    version = getVersion(size)
    
    # Finder patterns + divisor
    fillArea(matrix, 0, 0, 9, 9)
    fillArea(matrix, 0, size - 8, 8, 9)
    fillArea(matrix, size - 8, 0, 9, 8)
    # Alignment pattern - yes, we just place one. For the general
    # implementation, wait for the next parts in the series!
    fillArea(matrix, size - 9, size - 9, 5, 5)
    # Timing patterns
    fillArea(matrix, 6, 9, version * 4, 1)
    fillArea(matrix, 9, 6, 1, version * 4)
    # Dark module
    matrix[size - 8][8] = 1
    
    # Padding bits (fill since they aren't part of error correction)
    if size == 29:
        for row, col in [(i, 0) for i in range(17, 21)] + [(i, 1) for i in range (18, 21)]:
            matrix[row][col] = 1

    rowStep = -1
    
    row = size - 1
    column = size - 1
    sequence = []
    index = 0
    while (column >= 0):
        
        if (matrix[row][column] == 0):
            sequence.append((row, column))
    
    # Checking the parity of the index of the current module
    
        if index % 2 == 1:
            row += rowStep
            
            if (row == -1 or row == size):
                rowStep = -rowStep
                row += rowStep
                column -= 2 if column == 7 else 1
            else:
                column += 1
        else:
            column -= 1
        index += 1
    
    return sequence

def main():
    print(getModuleSequence(29))


if __name__ == "__main__":
    main()