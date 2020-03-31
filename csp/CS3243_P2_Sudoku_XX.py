import sys
import copy
from heapq import heappop, heappush, heapify

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def solve(self):
        visitedRows = [set() for i in range(9)]
        visitedCols = [set() for i in range(9)]
        visitedBlocks = [[set() for i in range(3)] for j in range(3)]
        possibleValues = [[set() for i in range(9)] for j in range(9)]
        isSafe = lambda row, col, num: (num not in visitedRows[row]) and (num not in visitedCols[col])  and (num not in visitedBlocks[row // 3][col // 3])

        # Initialize possible values of each cell
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0: # IsEmpty block
                    for k in range(1, 10):
                        possibleValues[i][j].add(k)
        
        for i in range(9):
            for j in range(9):
                num = puzzle[i][j]
                visitedRows[i].add(num)
                visitedCols[j].add(num)
                for k in range(9):
                    possibleValues[i][k].discard(num)
                    possibleValues[k][j].discard(num)

                x = i // 3
                y = j // 3
                visitedBlocks[x][y].add(num)

                x *= 3
                y *= 3
                for a in range(3):
                    for b in range(3):
                        possibleValues[x + a][y + b].discard(num)
                
        # set cells into arrays according to the number of unset cells they have
        setCells = []
        unsetCells = [[] for j in range(10)]

        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    size = len(possibleValues[i][j])
                    unsetCells[size].append((i, j))

        pq = []
        heapify(pq) 
        for i in range(10):
            if len(unsetCells[i]) > 0:
                heappush(pq, i)
        
        size = pq[0]
        if size == 0: # assumes puzzle is valid
            return self.ans
        
        # main solving loop
        currElement = unsetCells[size].pop()
        currR, currC = currElement 
        currVal = min(possibleValues[currR][currC])
        print(size)
        print(currElement)
        print(puzzle[currR][currC])
        while currVal <= 9 or len(setCells) > 0:
            if currVal in possibleValues[currR][currC]:
                print(currVal)
            currVal += 1

        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
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

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
