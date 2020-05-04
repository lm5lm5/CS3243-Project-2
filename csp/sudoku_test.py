import sys

if len(sys.argv) != 2:
        print ("\nUsage: python sudoku_test.py output.txt\n")
        raise ValueError("Wrong number of arguments!")

try:
    f = open(sys.argv[1], 'r')
except IOError:
    print ("\nUsage: python sudoku_test.py output.txt\n")
    raise IOError("Input file not found!")

puzzle = [[0 for i in range(9)] for j in range(9)]
lines = f.readlines()

i, j = 0, 0
for line in lines:
    for number in line:
        if '0' <= number <= '9':
            puzzle[i][j] = int(number)
            j += 1
            if j == 9:
                i += 1
                j = 0
    
isValid = True
for i in range(9):
    rowSet = set()
    colSet = set()
    for j in range(9):
        num = puzzle[i][j]
        rowSet.add(num)
        colSet.add(num)
    isValid = isValid and len(rowSet) == 9 and len(colSet) == 9

for r in range(0, 9, 3):
    for c in range(0, 9, 3):
        blockSet = set()
        for i in range(3):
            for j in range(3):
                num = puzzle[r + i][c + j]
                blockSet.add(num)
        isValid = isValid and len(blockSet) == 9

print("isValidSolution: " + str(isValid))