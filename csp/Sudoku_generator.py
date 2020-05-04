# Sudoku Generator Algorithm
import sys
import random

# initialise empty 9 by 9 grid
grid = [[0 for i in range(9)] for j in range(9)]


# A function to check if the grid is full
def checkGrid(grid):
    for row in range(0, 9):
        for col in range(0, 9):
            if grid[row][col] == 0:
                return False

    # We have a complete grid!
    return True


def checkValueNotInCol(value, currentGrid, col):
    return value not in (
        currentGrid[0][col], currentGrid[1][col], currentGrid[2][col],
        currentGrid[3][col], currentGrid[4][col], currentGrid[5][col],
        currentGrid[6][col], currentGrid[7][col], currentGrid[8][col])


def checkValueNotInSubgrid(value, currentGrid, row, col):
    if row < 3:
        if col < 3:
            square = [currentGrid[i][0:3] for i in range(0, 3)]
        elif col < 6:
            square = [currentGrid[i][3:6] for i in range(0, 3)]
        else:
            square = [currentGrid[i][6:9] for i in range(0, 3)]
    elif row < 6:
        if col < 3:
            square = [currentGrid[i][0:3] for i in range(3, 6)]
        elif col < 6:
            square = [currentGrid[i][3:6] for i in range(3, 6)]
        else:
            square = [currentGrid[i][6:9] for i in range(3, 6)]
    else:
        if col < 3:
            square = [currentGrid[i][0:3] for i in range(6, 9)]
        elif col < 6:
            square = [currentGrid[i][3:6] for i in range(6, 9)]
        else:
            square = [currentGrid[i][6:9] for i in range(6, 9)]
    # Check that this value has not already be used on this 3x3 square
    return value not in (square[0] + square[1] + square[2])


# A recursive function to check all possible combinations of numbers until a solution is found
# stop checking when 2 possible solutions are found
def solveGrid(grid):
    global counter
    if counter >= 2:
        return
    # Find next empty cell
    for i in range(0, 81):
        row = i // 9
        col = i % 9
        if grid[row][col] == 0:
            for value in range(1, 10):
                # Check that this value has not already be used on this row
                if not (value in grid[row]):
                    # Check that this value has not already be used on this column
                    if checkValueNotInCol(value, grid, col):
                        # Check that this value has not already be used on the subgrid
                        if checkValueNotInSubgrid(value, grid, row, col):
                            grid[row][col] = value
                            if checkGrid(grid):
                                counter += 1
                                break
                            else:
                                if solveGrid(grid):
                                    return True
            break
    grid[row][col] = 0


numberList = [(i + 1) for i in range(9)]


# shuffle(numberList)

# A recursive function to create a completely filled Sudoku puzzle from an empty grid
def fillGrid(grid):
    # Find next empty cell
    for i in range(0, 81):
        row = i // 9
        col = i % 9
        if grid[row][col] == 0:
            random.shuffle(numberList)
            for value in numberList:
                # Check that this value has not already be used on this row
                if not (value in grid[row]):
                    # Check that this value has not already be used on this column
                    if checkValueNotInCol(value, grid, col):
                        # Check that this value has not already be used on this column
                        if checkValueNotInSubgrid(value, grid, row, col):
                            grid[row][col] = value
                            if checkGrid(grid):
                                return True
                            else:
                                if fillGrid(grid):
                                    return True
            break
    grid[row][col] = 0


# Start Removing Numbers one by one

# A higher number of attempts will end up removing more numbers from the grid
# Potentially resulting in more difficult grids to solve!
def createSudoku(attempts):
    global counter
    while attempts > 0:
        # Select a random cell that is not already empty
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        while grid[row][col] == 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
        # Remember its cell value in case we need to put it back
        backup = grid[row][col]
        grid[row][col] = 0

        # Take a full copy of the grid
        copyGrid = []
        for r in range(0, 9):
            copyGrid.append([])
            for c in range(0, 9):
                copyGrid[r].append(grid[r][c])

        # Count the number of solutions that this grid has (using a backtracking approach implemented in the
        # solveGrid() function)
        counter = 0
        solveGrid(copyGrid)
        # If the number of solution is different from 1 then we need to cancel the change by putting the value we
        # took away back in the grid
        if counter != 1:
            grid[row][col] = backup
            # We could stop here, but we can also have another attempt with a different cell just to try to remove
            # more numbers
            attempts -= 1
    return grid


# Find a valid Sudoku puzzle until no more cell can be removed
def createSudokuNew():
    global counter
    filledCells = [i for i in range(81)]
    currentCellOptions = [i for i in range(81)]

    while len(currentCellOptions) != 0:
        # Select a random cell that is not already empty
        index = random.choice(currentCellOptions)
        row = index // 9
        col = index % 9
        # Remember its cell value in case we need to put it back
        backup = grid[row][col]
        grid[row][col] = 0

        # Take a full copy of the grid
        copyGrid = []
        for r in range(0, 9):
            copyGrid.append([])
            for c in range(0, 9):
                copyGrid[r].append(grid[r][c])

        # Count the number of solutions that this grid has (using a backtracking approach implemented in the
        # solveGrid() function)
        counter = 0
        solveGrid(copyGrid)
        # If the number of solution is different from 1 then we need to cancel the change by putting the value we
        # took away back in the grid
        if counter == 1:
            filledCells.remove(index)
            currentCellOptions = list(filledCells)
        else:
            grid[row][col] = backup
            currentCellOptions.remove(index)
    print("number of filled cells: " + str(len(filledCells)))
    return grid

# # Find a valid Sudoku puzzle until no more cell can be removed
# def createSudokuNewNew():
#     global counter
#     filledCells = [i for i in range(81)]
#     currentCellOptions = [i for i in range(81)]
#     nextLevelCellOptions = [i for i in range(81)]
#
#     # Select the first random cell to be removed, the puzzle is guaranteed to be valid
#     index = random.choice(currentCellOptions)
#     row = index // 9
#     col = index % 9
#     grid[row][col] = 0
#     currentCellOptions.remove(index)
#     nextLevelCellOptions.remove(index)
#
#     while len(currentCellOptions) != 0:
#         # Select a random cell that is not already empty
#         index = random.choice(currentCellOptions)
#         row = index // 9
#         col = index % 9
#         # Remember its cell value in case we need to put it back
#         backup = grid[row][col]
#         grid[row][col] = 0
#
#         # Take a full copy of the grid
#         copyGrid = []
#         for r in range(0, 9):
#             copyGrid.append([])
#             for c in range(0, 9):
#                 copyGrid[r].append(grid[r][c])
#
#         # Count the number of solutions that this grid has (using a backtracking approach implemented in the
#         # solveGrid() function)
#         counter = 0
#         solveGrid(copyGrid)
#         # If the number of solution is different from 1 then we need to cancel the change by putting the value we
#         # took away back in the grid
#         if counter == 1:
#             filledCells.remove(index)
#             currentCellOptions = list(filledCells)
#         else:
#             grid[row][col] = backup
#             currentCellOptions.remove(index)
#     print("number of filled cells: " + str(len(filledCells)))
#     return grid

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("\nUsage: python Sudoku_generator.py output.txt\n")
        raise ValueError("Wrong number of arguments!")

    fillGrid(grid)
    finalGrid = createSudokuNew()
    print("Sudoku Grid Ready")
    with open(sys.argv[1], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(finalGrid[i][j]) + " ")
            f.write("\n")
