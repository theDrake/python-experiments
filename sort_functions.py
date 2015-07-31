#!/usr/bin/env python

#------------------------------------------------------------------------------
#    Filename: sort_functions.py
#
#      Author: David C. Drake (http://davidcdrake.com)
#
# Description: A collection of sort functions -- bubble sort, shaker sort,
#              selection sort, quick sort, modified quick sort, merge sort, and
#              hash sort -- as well as helper functions to analyze the
#              effectiveness and efficiency of those functions. Developed using
#              Python 2.7.
#------------------------------------------------------------------------------

import sys
import random
import math


#------------------------------------------------------------------------------
#    Function: bubbleSort
#
# Description: Sorts a list using a "bubble sort" algorithm.
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def bubbleSort(list):
    totalComparisons, totalSwaps = (0, 0)

    (comparisons, swaps) = bubbleSortPass(list)
    totalComparisons += comparisons
    totalSwaps += swaps
    while (swaps > 0):
        (comparisons, swaps) = bubbleSortPass(list)
        totalComparisons += comparisons
        totalSwaps += swaps

    return (totalComparisons, totalSwaps)


#------------------------------------------------------------------------------
#    Function: bubbleSortPass
#
# Description: Performs one pass of a "bubble sort" on a list.
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def bubbleSortPass(list):
    comparisons, swaps = 0, 0

    for i in range(len(list) - 1):
        comparisons += 1
        if list[i] > list[i + 1]:
            list[i], list[i + 1] = list[i + 1], list[i]
            swaps += 1

    return (comparisons, swaps)


#------------------------------------------------------------------------------
#    Function: shakerSort
#
# Description: Sorts a list using a "shaker sort" algorithm.
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def shakerSort(list):
    totalComparisons, totalSwaps = 0, 0

    (comparisons, swaps) = shakerSortPass(list)
    totalComparisons += comparisons
    totalSwaps += swaps
    while (swaps > 0):
        (comparisons, swaps) = shakerSortPass(list)
        totalComparisons += comparisons
        totalSwaps += swaps

    return (totalComparisons, totalSwaps)


#------------------------------------------------------------------------------
#    Function: shakerSortPass
#
# Description: Performs one pass of a "shaker sort" on a list.
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def shakerSortPass(list):
    comparisons, swaps = 0, 0

    for i in range(len(list) - 1):
        comparisons += 1
        if list[i] > list[i + 1]:
            list[i], list[i + 1] = list[i + 1], list[i]
            swaps += 1
    for i in range(len(list) - 1, 0, -1):
        comparisons += 1
        if list[i] < list[i - 1]:
            list[i], list[i - 1] = list[i - 1], list[i]
            swaps += 1

    return (comparisons, swaps)


#------------------------------------------------------------------------------
#    Function: selectionSort
#
# Description: Sorts the elements of a list via the "selection sort" strategy.
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def selectionSort(list):
    comparisons, swaps = 0, 0

    for i in range(len(list) - 1):
        minIndex = i
        for j in range (i + 1, len(list)):
            comparisons += 1
            if list[j] < list[minIndex]:
                minIndex = j
        if minIndex != i:
            list[i], list[minIndex] = list[minIndex], list[i]
            swaps += 1

    return (comparisons, swaps)


#------------------------------------------------------------------------------
#    Function: quickSort
#
# Description: Sorts the elements of a list via the "quick sort" strategy.
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def quickSort(list):
    return quickSortOverRange(list, 0, len(list) - 1)


#------------------------------------------------------------------------------
#    Function: quickSortOverRange
#
# Description: Sorts a given range of a list via the "quick sort" strategy.
#
#      Inputs: list - The list to be sorted.
#              low  - Lower bound of the range; also the element against which
#                     other elements will be compared.
#              high - Upper bound of the range.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def quickSortOverRange(list, low, high):
    comparisons, swaps = 0, 0

    if high <= low:
        return (comparisons, swaps)

    # Divide the list/sub-list by comparison of each element to the value of
    # the first element:
    leftMostGreaterThan = low + 1
    for i in range(low + 1, high + 1):
        comparisons += 1
        if list[i] < list[low]:
            if i > low:
                list[i], list[leftMostGreaterThan] = \
                         list[leftMostGreaterThan], list[i]
                swaps += 1
            leftMostGreaterThan += 1

    # Move the first element (if necessary) so it can serve as the pivot point:
    if (leftMostGreaterThan - 1) > low:
        list[low], list[leftMostGreaterThan - 1] = \
                   list[leftMostGreaterThan - 1], list[low]
        swaps += 1

    # Split the list/sub-list at the pivot point and sort each half:
    (c, s) = quickSortOverRange(list, low, leftMostGreaterThan - 2)
    comparisons += c
    swaps += s
    (c, s) = quickSortOverRange(list, leftMostGreaterThan, high)
    comparisons += c
    swaps += s

    return (comparisons, swaps)


#------------------------------------------------------------------------------
#    Function: modifiedQuickSort
#
# Description: Sorts the elements of a list via the "modified quick sort"
#              strategy (the first and middles elements are swapped).
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def modifiedQuickSort(list):
    # Swap the first and middle elements:
    list[0], list[len(list) / 2] = list[len(list) / 2], list[0]
    (comparisons, swaps) = quickSortOverRange(list, 0, len(list) - 1)

    # Take the initial swap into account:
    return (comparisons, swaps + 1)


#------------------------------------------------------------------------------
#    Function: mergeSort
#
# Description: Sorts a list, or a range within a list, via the "merge sort"
#              strategy.
#
#      Inputs: list - The list to be sorted.
#              low  - Lower bound of the range to be sorted, inclusive (zero by
#                     default).
#              high - Upper bound of the range to be sorted, inclusive (length
#                     of the list minus one by default).
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def mergeSort(list, low=0, high=-1):
    totalComparisons, totalSwaps = 0, 0

    if high < 0:
        high = len(list) - 1

    if high - low < 2:
        totalComparisons += 1
        if list[low] > list[high]:
            list[low], list[high] = list[high], list[low]
            totalSwaps += 1
        return (totalComparisons, totalSwaps)

    mid = (high - low) / 2 + low

    # Sort the first half of the list/sub-list:
    (comparisons, swaps) = mergeSort(list, low, mid)
    totalComparisons += comparisons
    totalSwaps += swaps

    # Sort the second half of the list/sub-list:
    (comparisons, swaps) = mergeSort(list, mid + 1, high)
    totalComparisons += comparisons
    totalSwaps += swaps

    # Merge the two sorted halves in a new list:
    tempList = []
    i = low
    j = mid + 1
    while i <= mid and j <= high:
        totalComparisons += 1
        if list[i] < list[j]:
            tempList.append(list[i])
            i += 1
        else:
            tempList.append(list[j])
            j += 1
    while i <= mid:
        tempList.append(list[i])
        i += 1
    while j <= high:
        tempList.append(list[j])
        j += 1

    # Replace the original list/sub-list with the sorted list/sub-list:
    for i in range(len(tempList)):
        list[i + low] = tempList[i]
        totalSwaps += 1

    return (totalComparisons, totalSwaps)


#------------------------------------------------------------------------------
#    Function: hashSort
#
# Description: Sorts a list via the "hash sort" strategy. Assumes that each
#              value in the list will be less than the length of the list.
#
#      Inputs: list - The list to be sorted.
#
#     Outputs: A tuple containing the number of element comparisons and the
#              number of element swaps that occurred.
#------------------------------------------------------------------------------
def hashSort(list):
    comparisons, swaps = 0, 0

    hashTable = [0] * len(list)
    for value in list:
        hashTable[value] += 1

    j = 0
    for i in range(len(list)):
        while hashTable[j] < 1:
            j += 1
            comparisons += 1
        comparisons += 1
        if list[i] != j:
            list[i] = j
            swaps += 1
        hashTable[j] -= 1

    return (comparisons, swaps)


#------------------------------------------------------------------------------
#    Function: createRandomList
#
# Description: Creates a list of a given length whose elements are integers
#              randomly selected between 0 and the length of the list
#              (exclusive). Duplicate elements may occur and the list will not
#              be sorted.
#
#      Inputs: n - The length of the list as well as one more than the maximum
#                  value of its elements.
#
#     Outputs: A random list of 'n' integers between 0 and 'n' (exclusive).
#------------------------------------------------------------------------------
def createRandomList(n):
    randomList = []
    for i in range(n):
        randomList.append(random.randint(0, n - 1))

    return randomList


#------------------------------------------------------------------------------
#    Function: createMostlySortedList
#
# Description: Creates a list of a given length whose elements are integers
#              randomly selected between 0 and the length of the list
#              (exclusive; duplicate elements may occur), sorts the list, then
#              swaps the first and last elements.
#
#      Inputs: n - The length of the list as well as one more than the maximum
#                  value of its elements.
#
#     Outputs: A mostly sorted list of 'n' randomly generated integers between
#              0 and 'n' (exclusive).
#------------------------------------------------------------------------------
def createMostlySortedList(n):
    list = createRandomList(n)
    list[0], list[n - 1] = list[n - 1], list[0]

    return list


#------------------------------------------------------------------------------
#    Function: isSorted
#
# Description: Determines whether a given list is sorted (in ascending order).
#
#      Inputs: list - The list to be analyzed.
#
#     Outputs: 'True' if all the elements in the list are in ascending order,
#              'False' otherwise.
#------------------------------------------------------------------------------
def isSorted(list):
    for i in range(len(list) - 1):
        if list[i] > list[i + 1]:
            return False

    return True


#------------------------------------------------------------------------------
#    Function: compareLists
#
# Description: Compares two lists of equal length, returning the number of
#              differences between them.
#
#      Inputs: list1, list2 - The lists to be compared.
#
#     Outputs: The number of differences between the lists (or -1 if an error
#              is detected).
#------------------------------------------------------------------------------
def compareLists(list1, list2):
    if len(list1) != len(list2):
        print "Error: lists of unequal length passed to 'compareLists()'."
        return -1

    differences = 0
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            differences += 1

    return differences


#------------------------------------------------------------------------------
#    Function: testSortFunction
#
# Description: Tests a given sort function on a given list and prints test
#              results to the screen.
#
#      Inputs: sortFunction - The sort function to be tested.
#              list         - The list to be sorted (to test the function).
#              showLists    - If 'True', the list will be printed to the screen
#                             in both its original and sorted forms. ('False'
#                             by default.)
#
#     Outputs: 'True' if the list is sorted, 'False' otherwise. (Also prints
#              relevant information to the screen, such as the number of swaps
#              performed by the sort function, the number of differences
#              between the original list and its sorted version, and whether or
#              not the list was accurately sorted.)
#------------------------------------------------------------------------------
def testSortFunction(sortFunction, list, showLists=False):
    print 'Testing', str(sortFunction), 'on random list of length', \
          str(len(list)) + ':'

    # Copy the original list (to compare with the sorted list later):
    listCopy = []
    for e in list:
        listCopy.append(e)

    # Sort the list and display data regarding the effectiveness and efficiency
    # of the given sort function:
    (comparisons, swaps) = sortFunction(list)
    print '\tComparisons:\t' + str(comparisons)
    print '\tSwaps:\t\t' + str(swaps)
    print '\tDifferences:\t' + str(compareLists(list, listCopy))
    print '\tSorted:\t\t' + str(isSorted(list))
    if showLists:
        print '\tOriginal list:\t' + str(listCopy)
        print '\tSorted list:\t' + str(list)

    return isSorted(list)


#------------------------------------------------------------------------------
#    Function: testMultipleSortFunctions
#
# Description: Tests a given list of sort functions on multiple lists and
#              prints results to the screen.
#
#      Inputs: functionList - The list of sort functions to be tested.
#              testListSize - Size of lists to be created for testing functions
#                             as well as the upper limit (exclusive) on values
#                             within those lists (1000 by default).
#              iterations   - Number of test runs to perform on each function
#                             (1000 by default).
#              mostlySorted - If 'True', the functions will be tested on
#                             "mostly sorted" lists rather than completely
#                             random lists. ('False' by default.)
#
#     Outputs: A list containing the number of times each sort function failed
#              (with indices corresponding to those of the list of functions).
#------------------------------------------------------------------------------
def testMultipleSortFunctions(functionList,
                              testListSize=1000,
                              iterations=1000,
                              mostlySorted=False):
    failuresList = []

    for i in range(len(functionList)):
        failuresList.append(0)
        for j in range(iterations):
            if mostlySorted:
                list = createMostlySortedList(testListSize)
            else:
                list = createRandomList(testListSize)
            functionList[i](list)
            if not isSorted(list):
                failuresList[i] += 1

    return failuresList


#------------------------------------------------------------------------------
#    Function: storePerformanceDataForMultipleSortFunctions
#
# Description: Collects performance data for a given list of sort functions and
#              stores the results in a CSV (comma-separated values) file.
#
#      Inputs: filename     - Desired name for the output file.
#              functionList - A list of tuples, each containing a sort function
#                             followed by its name as a string.
#              iterations   - Number of times to run each test for each
#                             function (1000 by default).
#
#     Outputs: The number of tests performed, or -1 if an error occurs. (Also,
#              data is written to an output file.)
#------------------------------------------------------------------------------
def storePerformanceDataForMultipleSortFunctions(filename,
                                                 functionList,
                                                 iterations=1000):
    totalTests       = 0
    storeComparisons = True
    mostlySorted     = False
    done             = False

    fout = open(filename, 'w')
    if not fout:
        print 'Error: the file "' + filename + '" could not be opened.'
        return -1

    while not done:
        if storeComparisons:
            s = 'Comparisons'
        else:
            s = 'Swaps'
        if mostlySorted:
            s += ' on Mostly Sorted Data\n'
        else:
            s += ' on Random Data\n'

        fout.write(s)
        print s

        # Write column headers to the file:
        fout.write('Power of Two, ')
        for function in functionList:
            fout.write(function[1] + ', ')
        fout.write('\n')

        # Gather performance data and write them to the file:
        for powerOfTwo in range(3, 13):
            listSize = 2 ** powerOfTwo
            print '2^' + str(powerOfTwo)
            fout.write(str(powerOfTwo) + ', ')
            for function in functionList:
                print function[1]
                totalComparisons, totalSwaps = 0, 0
                for i in range(iterations):
                    if mostlySorted:
                        testList = createMostlySortedList(listSize)
                    else:
                        testList = createRandomList(listSize)
                    (comparisons, swaps) = function[0](testList)
                    totalComparisons += comparisons
                    totalSwaps += swaps
                    totalTests += 1
                if storeComparisons:
                    s = str(math.log(float(totalComparisons / iterations), 2))
                else:
                    s = str(math.log(float(totalSwaps / iterations), 2))
                fout.write(s + ', ')
            fout.write('\n')

        # Change settings for next test run:
        if storeComparisons:
            storeComparisons = False
        elif mostlySorted:
            done = True
        else:
            mostlySorted     = True
            storeComparisons = True
        fout.write('\n')

    fout.close()

    return totalTests


def main():
    sys.setrecursionlimit(100000)

    sortFunctions = [(bubbleSort, 'Bubble'),
                     (shakerSort, 'Shaker'),
                     (selectionSort, 'Selection'),
                     (quickSort, 'Quick'),
                     (modifiedQuickSort, 'MQuick'),
                     (mergeSort, 'Merge'),
                     (hashSort, 'Hash')]

    storePerformanceDataForMultipleSortFunctions('a.csv', sortFunctions, 10)

##    listSize       = 3
##    testIterations = 100
##
##    for function in sortFunctions:
##        randomList = createRandomList(listSize)
##        testSortFunction(function, randomList)
##
##    # Test each function with completely randomized lists:
##    print
##    failures = testMultipleSortFunctions(sortFunctions,
##                                         listSize,
##                                         testIterations)
##    for i in range(len(failures)):
##        print 'Failures for', str(sortFunctions[i]) + ':\n\t', \
##              str(failures[i]), '/', testIterations
##
##    # Test each function with mostly-sorted lists:
##    print
##    failures = testMultipleSortFunctions(sortFunctions,
##                                         listSize,
##                                         testIterations,
##                                         True)
##    for i in range(len(failures)):
##        print 'Failures for', str(sortFunctions[i]) + ':\n\t', \
##              str(failures[i]), '/', testIterations

if __name__ == '__main__':
    main()
