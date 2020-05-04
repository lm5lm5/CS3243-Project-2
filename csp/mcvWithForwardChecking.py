import sys
import copy
import time
from heapq import heappop, heappush, heapify

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def solve(self):
        visitedRows = [[False for j in range(10)] for i in range(9)]
        visitedCols = [[False for j in range(10)] for i in range(9)]
        visitedBlocks = [[[False for k in range(10)] for i in range(3)] for j in range(3)]
        possibleValues = [[set() for i in range(9)] for j in range(9)]
        isSafe = lambda row, col, num: (not visitedRows[row][num]) and (not visitedCols[col][num])  and (not visitedBlocks[row // 3][col // 3][num])
        isUnfilledCell = lambda row, col: self.ans[row][col] == 0

        # Initialize possible values of each cell
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0: # IsEmpty block
                    for k in range(1, 10):
                        possibleValues[i][j].add(k)

        for i in range(9):
            for j in range(9):
                num = puzzle[i][j]
                visitedRows[i][num] = True
                visitedCols[j][num] = True
                for k in range(9):
                    possibleValues[i][k].discard(num)
                    possibleValues[k][j].discard(num)

                x = i // 3
                y = j // 3
                visitedBlocks[x][y][num] = True

                x *= 3
                y *= 3
                for a in range(3):
                    for b in range(3):
                        possibleValues[x + a][y + b].discard(num)

        setCells = []                           # stack of set cells
        unsetCells = [set() for j in range(10)] # set cells into lists according to the domain size of the cell
        hasUnfilledCells = False

        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    size = len(possibleValues[i][j])
                    unsetCells[size].add((i, j))
                    hasUnfilledCells = True

        if not hasUnfilledCells:
            return self.ans

        def discardNumFromDomain(row, col, num): # Returns true if the discard did not lead an empty domain i.e. will fail later
            if isUnfilledCell(row, col):
                cell = (row, col)
                prevLen = len(possibleValues[row][col])
                unsetCells[prevLen].discard(cell)
                possibleValues[row][col].discard(num)
                newLen = len(possibleValues[row][col])
                unsetCells[newLen].add(cell)
                return newLen > 0
            return True

        def addBackNumToDomain(row, col, num):
            if isUnfilledCell(row, col) and isSafe(row, col, num):
                cell = (row, col)
                prevLen = len(possibleValues[row][col])
                unsetCells[prevLen].discard(cell)
                possibleValues[row][col].add(num)
                newLen = len(possibleValues[row][col])
                unsetCells[newLen].add(cell)


        def getNextUnsetCell():
            for i in range(len(unsetCells)):
                if len(unsetCells[i]) > 0:
                    cell = unsetCells[i].pop()
                    return cell

        currElement = getNextUnsetCell()
        currR, currC = currElement
        currVal = 1

        # Main backtracking loop
        while currVal <= 9 or len(setCells) > 0:
            while currVal <= 9 and currVal not in possibleValues[currR][currC]:
                currVal += 1

            if currVal <= 9:
                self.ans[currR][currC] = currVal
                visitedRows[currR][currVal] = True
                visitedCols[currC][currVal] = True
                blockR = currR // 3
                blockC = currC // 3
                visitedBlocks[blockR][blockC][currVal] = True

                isPossibleValue = True

                # Forward checking
                for i in range(9):
                    if currVal in possibleValues[currR][i]:
                        isPossibleValue = isPossibleValue and discardNumFromDomain(currR, i, currVal)
                    if currVal in possibleValues[i][currC]:
                        isPossibleValue = isPossibleValue and discardNumFromDomain(i, currC, currVal)
                    if not isPossibleValue:
                        break

                blockR *= 3
                blockC *= 3
                for i in range(3):
                    for j in range(3):
                        a = blockR + i
                        b = blockC + j
                        if currVal in possibleValues[a][b]:
                            isPossibleValue = isPossibleValue and discardNumFromDomain(a, b, currVal)
                        if not isPossibleValue:
                                break
                    if not isPossibleValue:
                            break
                    

                setCells.append((currR, currC, currVal))

                nextUnsetCell = getNextUnsetCell()

                if nextUnsetCell == None:
                    return self.ans

                currR, currC = nextUnsetCell
                currVal =  1 if isPossibleValue else 10

            elif len(setCells) > 0: # Backtrack if no more available numbers
                self.ans[currR][currC] = 0 # reset to unfilled cell
                currR, currC, currVal = setCells.pop()
                visitedRows[currR][currVal] = False
                visitedCols[currC][currVal] = False
                blockR = currR // 3
                blockC = currC // 3
                visitedBlocks[blockR][blockC][currVal] = False

                # Reverse the forward checking
                for i in range(9):
                    addBackNumToDomain(currR, i, currVal)
                    addBackNumToDomain(i, currC, currVal)

                blockR *= 3
                blockC *= 3
                for i in range(3):
                    for j in range(3):
                        addBackNumToDomain(blockR + i, blockC + j, currVal)

                currVal += 1

        return None

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

    start_time = time.time()

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

    print("time elapsed in seconds: %s" % (time.time() - start_time))

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
