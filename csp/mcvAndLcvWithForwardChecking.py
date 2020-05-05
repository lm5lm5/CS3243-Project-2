import sys
import copy
import time
from heapq import heappop, heappush, heapify

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

import collections

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def solve(self):
        nine = 9
        visitedRows = [[False for j in range(10)] for i in range(9)]
        visitedCols = [[False for j in range(10)] for i in range(9)]
        visitedBlocks = [[[False for k in range(10)] for i in range(3)] for j in range(3)]
        possibleValues = [[[False for k in range(10)] for i in range(9)] for j in range(9)]
        possibleValuesCounter = [[9 for j in range(9)] for i in range(9)]
        isSafe = lambda row, col, num: (not visitedRows[row][num]) and (not visitedCols[col][num])  and (not visitedBlocks[row // 3][col // 3][num])
        isUnfilledCell = lambda row, col: self.ans[row][col] == 0

        # Initialize possible values of each cell
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0: # IsEmpty block
                    for k in range(1, 10):
                        possibleValues[i][j][k] = True
        
        for i in range(9):
            for j in range(9):
                num = puzzle[i][j]
                if num != 0:
                    visitedRows[i][num] = True
                    visitedCols[j][num] = True
                    for k in range(9):
                        if possibleValues[i][k][num]:
                            possibleValues[i][k][num] = False
                            possibleValuesCounter[i][k] -= 1
                        if possibleValues[k][j][num]:
                            possibleValues[k][j][num] = False
                            possibleValuesCounter[k][j] -= 1

                    x = i // 3
                    y = j // 3
                    visitedBlocks[x][y][num] = True

                    x *= 3
                    y *= 3
                    for a in range(3):
                        for b in range(3):
                            s = x + a
                            t = y + b
                            if possibleValues[s][t][num]:
                                possibleValues[s][t][num] = False
                                possibleValuesCounter[s][t] -= 1

        possibleValuesList = [[list() for j in range(9)] for i in range(9)]
        for i in range(9):
            for j in range(9):
                for k in range(9, 0, -1):
                    if possibleValues[i][j][k]:
                        possibleValuesList[i][j].append(k)

        setCells = []                           # stack of set cells
        unsetCells = [OrderedSet() for j in range(10)] # set cells into lists according to the domain size of the cell
        hasUnfilledCells = False

        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    size = possibleValuesCounter[i][j]
                    unsetCells[size].add(i * nine + j)
                    hasUnfilledCells = True

        if not hasUnfilledCells:
            return self.ans

        def discardNumFromDomain(row, col, num): # Returns true if the discard did not lead an empty domain i.e. will fail later
            cell = row * nine + col
            unsetCells[possibleValuesCounter[row][col]].discard(cell)
            possibleValues[row][col][num] = False
            possibleValuesCounter[row][col] -= 1
            newLen = possibleValuesCounter[row][col]
            unsetCells[newLen].add(cell)
            return newLen > 0
            

        def addBackNumToDomain(row, col, num):
            cell = row * nine + col
            prevLen = possibleValuesCounter[row][col]
            unsetCells[prevLen].discard(cell)
            possibleValues[row][col][num] = True
            possibleValuesCounter[row][col] += 1
            newLen = possibleValuesCounter[row][col]
            unsetCells[newLen].add(cell)

        constraintCounter = [0 for j in range(10)] # LCV
        def sortDomain(row, col):
            domainToSort = possibleValuesList[row][col]
            for num in domainToSort:
                constraintCounter[num] = 0
            blockR = (row // 3) * 3
            blockC = (col // 3) * 3

            for i in range(3):
                for j in range(3):
                    a = blockR + i
                    b = blockC + j
                    for num in domainToSort:
                        if isUnfilledCell(a, b) and possibleValues[a][b][num]:
                            constraintCounter[num] += 1
            for i in range(blockR):
                if isUnfilledCell(i, col) and possibleValues[i][col][num]:
                    constraintCounter[num] += 1
            for i in range(blockR + 3, 9):
                if isUnfilledCell(i, col) and possibleValues[i][col][num]:
                    constraintCounter[num] += 1       
            for i in range(blockC):
                if isUnfilledCell(row, i) and possibleValues[row][i][num]:
                    constraintCounter[num] += 1  
            for i in range(blockC + 3, 9):
                if isUnfilledCell(row, i) and possibleValues[row][i][num]:
                    constraintCounter[num] += 1 

            domainToSort.sort(key=lambda x: constraintCounter[x])

        def getNextUnsetCell():
            for i in range(len(unsetCells)):
                if len(unsetCells[i]) > 0:
                    return unsetCells[i].pop()

        currElement = getNextUnsetCell()
        currR = currElement // nine
        currC = currElement % nine
        sortDomain(currR, currC)
        index = 0

        backtracks = 0
        # Main backtracking loop
        while True:
            length = len(possibleValuesList[currR][currC])
            while index < length:
                currVal = possibleValuesList[currR][currC][index]
                if possibleValues[currR][currC][currVal]:
                    break
                else:
                    index += 1

            if index < length:
                self.ans[currR][currC] = currVal
                visitedRows[currR][currVal] = True
                visitedCols[currC][currVal] = True
                
                blockR = currR // 3
                blockC = currC // 3
                visitedBlocks[blockR][blockC][currVal] = True
                blockR *= 3
                blockC *= 3

                isPossibleValue = True

                # Forward checking
                if isPossibleValue:
                    for i in range(3):
                        for j in range(3):
                            a = blockR + i
                            b = blockC + j
                            if isUnfilledCell(a, b) and possibleValues[a][b][currVal] and not discardNumFromDomain(a, b, currVal):
                                isPossibleValue = False
                                break
                if isPossibleValue:
                    for i in range(blockR):
                        if isUnfilledCell(i, currC) and possibleValues[i][currC][currVal] and not discardNumFromDomain(i, currC, currVal):
                            isPossibleValue = False
                            break
                if isPossibleValue:
                    for i in range(blockR + 3, 9):
                        if isUnfilledCell(i, currC) and possibleValues[i][currC][currVal] and not discardNumFromDomain(i, currC, currVal):
                            isPossibleValue = False
                            break
                if isPossibleValue:
                    for i in range(blockC):
                        if isUnfilledCell(currR, i) and possibleValues[currR][i][currVal] and not discardNumFromDomain(currR, i, currVal):
                            isPossibleValue = False
                            break
                if isPossibleValue:
                    for i in range(blockC + 3, 9):
                        if isUnfilledCell(currR, i) and possibleValues[currR][i][currVal] and not discardNumFromDomain(currR, i, currVal):
                            isPossibleValue = False
                            break
              
                        

                setCells.append(currR * 100 + currC * 10 + index)

                nextUnsetCell = getNextUnsetCell()

                if nextUnsetCell == None:
                    print("backtracks ", backtracks)
                    return self.ans

                currR = nextUnsetCell // nine
                currC = nextUnsetCell % nine
                sortDomain(currR, currC)
                index = 0 if isPossibleValue else 10

            elif len(setCells) > 0: # Backtrack if no more available numbers
                backtracks += 1
                self.ans[currR][currC] = 0 # reset to unfilled cell
                x = setCells.pop()
                currR = (x // 100) % 10
                currC = (x // 10) % 10
                index = x % 10
                currVal = possibleValuesList[currR][currC][index]
                visitedRows[currR][currVal] = False
                visitedCols[currC][currVal] = False
                blockR = currR // 3
                blockC = currC // 3
                visitedBlocks[blockR][blockC][currVal] = False

                # Reverse the forward checking
                for i in range(9):
                    if isUnfilledCell(currR, i) and not possibleValues[currR][i][currVal] and isSafe(currR, i, currVal):
                        addBackNumToDomain(currR, i, currVal)
                    if isUnfilledCell(i, currC) and not possibleValues[i][currC][currVal] and isSafe(i, currC, currVal):
                        addBackNumToDomain(i, currC, currVal)

                blockR *= 3
                blockC *= 3
                for i in range(3):
                    for j in range(3):
                        a = blockR + i
                        b = blockC + j
                        if isUnfilledCell(a, b) and not possibleValues[a][b][currVal] and isSafe(a, b, currVal):
                            addBackNumToDomain(a, b, currVal)

                index += 1

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
