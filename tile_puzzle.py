#!/usr/bin/python2

#-------------------------------------------------------------------------------
#    Filename: tile_puzzle.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Solves a 3x3 tile-shifting puzzle.
#-------------------------------------------------------------------------------

import sys
from Queue import *

class Graph:
    def __init__(self, filename=None):
        self.__adjacencyList = []
        if filename:
            self.loadFromFile(filename)

    def __str__(self):
        return str(self.__adjacencyList)

    def addVertex(self):
        self.__adjacencyList.append([])

    def addEdge(self, v1, v2):
        if v1 >= len(self.__adjacencyList) or \
           v2 >= len(self.__adjacencyList) or \
           v1 == v2:
            return False
        self.__adjacencyList[v1].append(v2)
        self.__adjacencyList[v2].append(v1)
        return True

    def removeEdge(self, v1, v2):
        if v1 >= len(self.__adjacencyList):
            return False
        for i in range(len(self.__adjacencyList[v1])):
            if self.__adjacencyList[v1][i] == v2:
                self.__adjacencyList[v1].pop[i]
                return True
        return False

    def hasEdge(self, v1, v2):
        if v1 >= len(self.__adjacencyList) or \
           v2 >= len(self.__adjacencyList):
            return False
        for i in range(len(self.__adjacencyList[v1])):
            if self.__adjacencyList[v1][i] == v2:
                return True
        return False

    def getAdjacentVertices(self, v):
        if v >= len(self.__adjacencyList):
            return None
        vertices = []
        for i in range(len(self.__adjacencyList[v])):
            vertices.append(self.__adjacencyList[v][i])
        return vertices

    def getPath(self, v1, v2, depthFirst=True):
        if depthFirst:
            return self.depthFirstSearch(v1, v2)
        return self.breadthFirstSearch(v1, v2)

    def depthFirstSearch(self, v1, v2):
        if v1 >= len(self.__adjacencyList) or \
           v2 >= len(self.__adjacencyList):
            return None
        path = []
        self.depthFirstSearchR(v1, v2, path)
        return path

    def depthFirstSearchR(self, v1, v2, path):
        if v1 >= len(self.__adjacencyList) or \
           v2 >= len(self.__adjacencyList) or \
           v1 in path:
            return False
        print 'v1: ' + str(v1)
        path.append(v1)
        if v2 in path:
            return True
        for v in self.__adjacencyList[v1]:
            self.depthFirstSearchR(v, v2, path)
        if v2 in path:
            return True
        path.remove(v1)
        return False

    def breadthFirstSearch(self, v1, v2):
        if v1 >= len(self.__adjacencyList) or \
           v2 >= len(self.__adjacencyList):
            return None
        depth = 0
        path = []
        q = Queue()
        q.put(v1)
        while not q.empty():
            v = q.get()
            path.append(v)
            if v == v2:
                return path
            depth = depth + 1
            for adjacentV in self.getAdjacentVertices(v):
                if adjacentV not in path:
                    q.put(adjacentV)
        if v2 not in path:
            return []
        return path

    def loadFromFile(self, filename):
        self.__adjacencyList = []
        fin = open(filename, 'r')
        contents = fin.readlines()
        fin.close()
        if len(contents) < 2:
            print 'Error: invalid file.'
            return False
        numVertices = int(contents[0])
        numEdges = int(contents[1])
        numTestCases = int(contents[numEdges + 2])
        for i in range(numVertices):
            self.addVertex()
        for i in range(2, numEdges + 2):
            edge = contents[i].split()
            self.addEdge(int(edge[0]), int(edge[1]))
        testCases = []
        for i in range(numEdges + 3, len(contents)):
            test = contents[i].split()
            testCases.append((int(test[0]), int(test[1]), int(test[2])))
        failedTestCases = 0
        for t in testCases:
            path = self.getPath(t[0], t[1])
            if len(path) != t[2]:
                print 'Test case ' + str(t) + ' failed. Path of length ' + \
                      str(len(path)) + ' found:\n\t' + str(path)
                failedTestCases += 1
        if failedTestCases > 0:
            return False
        return True

    def isConnected(self):
        for i in range(len(self.__adjacencyList)):
            for j in range(i, len(self.__adjacencyList)):
                if not self.getPath(i, j):
                    return False
        return True

def main():
    sys.setrecursionlimit(100000)
    g = Graph("input.txt")
    print 'Graph data: ' + str(g)
    #print 'Connected? ' + str(g.isConnected())

if __name__ == '__main__':
    main()
