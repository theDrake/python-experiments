#!/usr/bin/python2

#-------------------------------------------------------------------------------
#    Filename: maze_solver.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Creates a random maze, then draws its solution. Developed using
#              Python 2.7 and graphics.py, which is available here:
#              http://mcsp.wartburg.edu/zelle/python/
#-------------------------------------------------------------------------------

from graphics import *
from time import sleep
from random import seed, randrange
from sys import setrecursionlimit

NUM_COLUMNS = 20
NUM_ROWS = 20
CELL_SIZE = 500 / NUM_COLUMNS
MARGIN = 10 / NUM_ROWS
SCREEN_WIDTH = NUM_COLUMNS * CELL_SIZE + 2 * MARGIN
SCREEN_HEIGHT = NUM_ROWS * CELL_SIZE + 2 * MARGIN
ANIMATION_DELAY = 0.01
RECURSION_LIMIT = 100000

class Cell:
    def __init__(self):
        self.left = self.top = self.right = self.bottom = True
        self.visited = False

    def Draw(self, win, i, j):
        x1 = MARGIN + i * CELL_SIZE
        y1 = MARGIN + j * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        if self.left:
            line = Line(Point(x1, y1), Point(x1, y2))
            if win.isOpen():
                line.draw(win)
        if self.top:
            line = Line(Point(x1, y1), Point(x2, y1))
            if win.isOpen():
                line.draw(win)
        if self.right:
            line = Line(Point(x2, y1), Point(x2, y2))
            if win.isOpen():
                line.draw(win)
        if self.bottom:
            line = Line(Point(x1, y2), Point(x2, y2))
            if win.isOpen():
                line.draw(win)

class Maze:
    def __init__(self):
        self.cells = []
        for i in range(NUM_COLUMNS):
            cellColumn = []
            for j in range(NUM_ROWS):
                cellColumn.append(Cell())
            self.cells.append(cellColumn)
        self.VisitR(0, 0)

        # Define the start of the maze:
        self.start = (0, 0)
        self.cells[self.start[0]][self.start[1]].top = False

        # Define the end of the maze:
        self.finish = (NUM_COLUMNS - 1, NUM_ROWS - 1)
        self.cells[self.finish[0]][self.finish[1]].bottom = False

    def VisitR(self, i, j):
        self.cells[i][j].visited = True
        while True:
            nexti = []
            nextj = []

            # Determine which cells we can move to next:
            if i > 0 and not self.cells[i - 1][j].visited: # left
                nexti.append(i - 1)
                nextj.append(j)
            if i < NUM_COLUMNS - 1 and \
              not self.cells[i + 1][j].visited: # right
                nexti.append(i + 1)
                nextj.append(j)
            if j > 0 and not self.cells[i][j - 1].visited: # up
                nexti.append(i)
                nextj.append(j - 1)
            if j < NUM_ROWS - 1 and not self.cells[i][j + 1].visited: # down
                nexti.append(i)
                nextj.append(j + 1)

            if len(nexti) == 0 and len(nextj) == 0:
                return

            # Randomly choose which direction to go:
            index = randrange(len(nexti))
            ni = nexti[index]
            nj = nextj[index]

            # Knock out walls between this cell and the next:
            if ni == i + 1: # right
                self.cells[i][j].right = self.cells[i + 1][j].left = False
            if ni == i - 1: # left
                self.cells[i][j].left = self.cells[i - 1][j].right = False
            if nj == j + 1: # bottom
                self.cells[i][j].bottom = self.cells[i][j + 1].top = False
            if nj == j - 1: # top
                self.cells[i][j].top = self.cells[i][j - 1].bottom = False

            # Recursively visit the next cell:
            self.VisitR(ni, nj)

    def Draw(self, win):
        for i in range(NUM_COLUMNS):
            for j in range(NUM_ROWS):
                if win.isOpen():
                    self.cells[i][j].Draw(win, i, j)
                else:
                    return
        sleep(ANIMATION_DELAY)

    def Solve(self):
        self.mMoves = []
        for i in range(NUM_COLUMNS):
            for j in range(NUM_ROWS):
                self.cells[i][j].visited = False
        self.SolveR(self.start[0], self.start[1])

    # Returns 'True' if the cell at (i, j) leads toward the exit.
    def SolveR(self, i, j):
        self.cells[i][j].visited = True
        self.mMoves.append((i, j))

        # Check for successful completion of the maze:
        if (i, j) == self.finish:
            return True

        # Try left:
        if i - 1 >= 0 and \
          not self.cells[i][j].left and \
          not self.cells[i - 1][j].visited:
            if self.SolveR(i - 1, j):
                return True

        # Try right:
        if i + 1 < NUM_COLUMNS and \
          not self.cells[i][j].right and \
          not self.cells[i + 1][j].visited:
            if self.SolveR(i + 1, j):
                return True

        # Try down:
        if j + 1 < NUM_ROWS and \
          not self.cells[i][j].bottom and \
          not self.cells[i][j + 1].visited:
            if self.SolveR(i, j + 1):
                return True

        # Try up:
        if j - 1 >= 0 and \
          not self.cells[i][j].top and \
          not self.cells[i][j - 1].visited:
            if self.SolveR(i, j - 1):
                return True

        # Dead end:
        self.mMoves.pop()#remove((i, j))
        return False

    def DrawSolution(self, win):
        print self.mMoves
        for (i, j) in self.mMoves:
            point = Point(i * CELL_SIZE + CELL_SIZE / 2,
                          j * CELL_SIZE + CELL_SIZE / 2)
            radius = CELL_SIZE / 8
            circle = Circle(point, radius)
            circle.setFill(color_rgb(0, 0, 0))
            if win.isOpen():
                circle.draw(win)
            else:
                return
            sleep(ANIMATION_DELAY)

def main():
    setrecursionlimit(RECURSION_LIMIT)
    seed()
    win = GraphWin("Maze Solver", SCREEN_WIDTH, SCREEN_HEIGHT)
    theMaze = Maze()
    if win.isOpen():
        theMaze.Draw(win)
    theMaze.Solve()
    if win.isOpen():
        theMaze.DrawSolution(win)
    if win.isOpen():
        win.getMouse()
        win.close()

if __name__ == '__main__':
    main()
