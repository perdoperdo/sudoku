import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy

class Sudoku:
    """Base Sudoku class"""

    def __init__(self, sudoku):
        self.puzzle = self.fromTextTuple(sudoku)
        self.originalPuzzle = self.puzzle.copy()
        self.initGroups()
        self.overlappingGroups = []
        for group1 in self.groups:
            for group2 in self.groups:
                if group1 != group2:
                    overlap = group1["cells"].intersection(group2["cells"])
                    if len(overlap) > 1:
                        self.overlappingGroups.append( (group1["name"], group2["name"]) )
        self.initPossibilities()
        self.eliminationSteps = {} # stats for solutions

    def fromTextTuple(self, sudoku):
        puzzle = dict()
        if (len(sudoku) != 9):
            raise Exception('Need 9 rows')
        for r in range(9):
            arow = sudoku[r]
            if (len(arow) != 9):
                raise Exception('Need 9 cells in row ' + str(r + 1) + ': \"' + arow + '"')
            for c in range(9):
                if arow[c] == ' ' or arow[c] == '.':
                    pass
                elif arow[c] >= '1' and arow[c] <= '9':
                    puzzle[(r, c)] = int(arow[c])
                else:
                    raise Exception('Unrecognized character ' + arow[c] + ' at row ' + str(r + 1) + " col " + str(
                        c + 1) + ': \"' + arow + '"')
        return puzzle

    def initGroups(self):
        allrows = list()
        allcols = list()
        allsquares = list()
        self.emptycells = set()
        for x in range(9):
            allrows.append({"name": "row " + str(1 + x), "cells": set()})
            allcols.append({"name": "col " + str(1 + x), "cells": set()})
            allsquares.append({"name": "sqr " + str(1 + x), "cells": set()})
        for i in range(9):
            for j in range(9):
                cell = (i, j)
                allrows[i]["cells"].add(cell)
                allcols[j]["cells"].add(cell)
                allsquares[3 * (i // 3) + (j // 3)]["cells"].add(cell)
                if not cell in self.puzzle:
                    self.emptycells.add(cell)
        # TODO make a dict and iterate over items, forget "cells" and "name" attributes
        # like for key, value in a_dict.items():
        self.groups = allrows + allcols + allsquares

    def initPossibilities(self):
        self.possibilities = dict()
        self.explanations = dict()
        for cell in self.emptycells:
            self.possibilities[cell] = set(range(1, 10))
            self.explanations[cell] = []

    def isCompleted(self):
        return len(self.emptycells) == 0

    def place(self, digit, cellAsString):
        if len(cellAsString) != 4:
            raise Exception('Place format is 4 characters R<row>C<col>')
        row = int(cellAsString[1])-1
        col = int(cellAsString[3])-1
        cell = (row,col)
        print("Place " + str(digit) + " at " + self.celltostr(cell))
        self.puzzle[cell] = digit
        self.emptycells.remove(cell)
        self.initPossibilities()

    def print(self):
        print(self.groups)
        print(str(len(self.groups)) + " groups")
        print(self.overlappingGroups)

    def getShowRaster(self):
        mx = np.zeros((9, 9))
        # color some squares to highlight the structure
        for x in range(0, 3):
            for y in range(0, 3):
                mx[x, y] = 1
                mx[x + 6, y] = 1
                mx[x, y + 6] = 1
                mx[x + 6, y + 6] = 1
                mx[x + 3, y + 3] = 1
        return mx

    def show(self):
        fig, ax = plt.subplots()
        im = ax.imshow(self.getShowRaster(), cmap="Purples",
                       alpha=0.6)  # strange way to plot a grid - need something simpler...
        # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
        # All ticks and label them with the respective list entries
        ax.set_xticks(np.arange(9))
        ax.set_yticks(np.arange(9))
        ax.set_xticklabels(range(1, 10))
        ax.set_yticklabels(range(1, 10))
        for cell in self.puzzle:
            ax.text(cell[1], cell[0], self.puzzle[cell], ha="center", va="center",
                    color= ("black" if (cell in self.originalPuzzle) else "blue"), size=15)
        for cell in self.emptycells:
            p = self.possibilities[cell]
            txt = "\n".join(["".join((str(i) if (i in p) else ".") for i in range(1, 4)),
                             "".join((str(i) if (i in p) else ".") for i in range(4, 7)),
                             "".join((str(i) if (i in p) else ".") for i in range(7, 10))])
            ax.text(cell[1], cell[0], txt, ha="center", va="center", color="black", size=9, alpha=0.6,
                    family='monospace')
        for x in range(8):
            if x == 2 or x == 5:
                pass
            else:
                plt.axhline(0.5 + x, color="grey")
                plt.axvline(0.5 + x, color="grey")
        for x in range(8):
            if x == 2 or x == 5:
                plt.axhline(0.5 + x, color="black")
                plt.axvline(0.5 + x, color="black")
        ax.set_title("Sudoku")
        fig.tight_layout()
        plt.show()

    # Make sure all groups are correct
    def check(self):
        pass

    def celltostr(self, pair):
        return "R"+str(1 + pair[0]) + "C" + str(1 + pair[1])

    def cellstostr(self, pairs):
        return str([self.celltostr(x) for x in pairs])

    def getMoves(self):
        possibleMoves = dict()
        for cell in self.emptycells:
            p = self.possibilities[cell]
            if (len(p) == 1):
                d = list(p)[0]
                if cell in possibleMoves:
                    if possibleMoves[cell]["move"] == d:
                        # just add another reason for the same move
                        possibleMoves[cell]["reasons"].append({"method" : "single cell value",
                                                               "reason" : self.explanations[cell]})
                    else:
                        # inconsistent results
                        raise Exception("ERROR! Found different move than " + str(d) + " at " + self.celltostr(cell))
                else:
                    possibleMoves[cell] = {"move" : d,
                                           "reasons" : [{"method" : "single cell value",
                                                         "reason" : self.explanations[cell]}]}
        for group in self.groups:
            for d in range(1,10):
                onlyPossibileCellInGroup = None
                nPossibilitiesInGroup = 0
                emptyCellsInGroup = group["cells"].intersection(self.emptycells)
                for cell in emptyCellsInGroup:
                    if d in self.possibilities[cell]:
                        onlyPossibileCellInGroup = cell
                        nPossibilitiesInGroup = nPossibilitiesInGroup + 1
                if nPossibilitiesInGroup == 1:
                    # reasons why d is excluded in all other cells in the group
                    # for all other cells get explanations x
                    # if x[1] contains d then add x[0] to reason why d is excluded
                    detailedReasons = {}
                    emptyCellsInGroup.remove(onlyPossibileCellInGroup)
                    for cell in emptyCellsInGroup:
                        for x in self.explanations[cell]:
                            if d in x["eliminations"]:
                                detailedReasons[ x["method"] + str(x["detail"]) ] = {"method" : x["method"], "detail" : x["detail"]}
                    if not onlyPossibileCellInGroup in possibleMoves:
                        possibleMoves[onlyPossibileCellInGroup] = {"move": d, "reasons": []}
                    if possibleMoves[onlyPossibileCellInGroup]["move"] == d:
                        # just add another reason for the same move
                        possibleMoves[onlyPossibileCellInGroup]["reasons"].append({"method" : "only place in " + group["name"],
                                                                                   "reason" : detailedReasons.values()})
                    else:
                        raise Exception("ERROR! Found different move than " + str(d) + " at " + self.celltostr(onlyPossibileCellInGroup))
        return possibleMoves

    # Updates cell candidates and reports on this
    def updateCandidates(self, cell, methodName, methodDetail, eliminations):
        candidates = self.possibilities[cell]
        commonElements = candidates.intersection(eliminations)
        if len(commonElements) > 0:
            if not methodName in self.eliminationSteps:
                self.eliminationSteps[methodName] = 0
            self.eliminationSteps[methodName] =\
                self.eliminationSteps[methodName] + len(commonElements)
            self.explanations[cell].append({"method": methodName,
                                            "detail": methodDetail,
                                            "eliminations": sorted(commonElements)})
            self.possibilities[cell] = candidates - commonElements

    # Filters the existing possibilities per cell by applying elimination
    # from all groups that this cell is part of. Basis is simple but we also
    # want to process the group that provides the largest nr of eliminations
    # first, so this becomes an iterative process.
    def groupElimination(self):
        #print('Simple elimination per cell')
        for cell in self.emptycells:
            while True:
                highestNrOfIntersections = 0
                groupWithHighestNrOfIntersections = None
                candidates = self.possibilities[cell]
                for agroup in self.groups:
                    if cell in agroup["cells"]:
                        digitsingroup = set([self.puzzle[c] for c in agroup["cells"] if c in self.puzzle])
                        commonelements = candidates.intersection(digitsingroup)
                        if len(commonelements) > highestNrOfIntersections:
                            highestNrOfIntersections = len(commonelements)
                            groupWithHighestNrOfIntersections = agroup
                if highestNrOfIntersections == 0:
                    break # Done - no more intersections to be found
                digitsingroupWithHighestNrOfIntersections = set([self.puzzle[c] for c in groupWithHighestNrOfIntersections["cells"] if c in self.puzzle])
                self.updateCandidates(cell, "simple elimination",
                                      groupWithHighestNrOfIntersections["name"],
                                      digitsingroupWithHighestNrOfIntersections)

    # Filters the existing possibilities by checking if there are subgroups
    # in each group that all have the same possibilities (complete subgroups). So
    # if there are three cells in a group with all {1,7,8} then we are sure these
    # values can only exist there and 1, 7 and 8 can be removed from all other
    # possibilities in the cells of this group.
    def perfectSubgroupElimination(self):
        for agroup in self.groups:
            subgroups = dict()
            subgroupPossibilities = dict()
            for cell in agroup["cells"]:
                if cell in self.emptycells:
                    possibilitiesKey = str(sorted(self.possibilities[cell]))
                    if not possibilitiesKey in subgroups:
                        subgroups[possibilitiesKey] = set()
                        subgroupPossibilities[possibilitiesKey] = set(sorted(self.possibilities[cell]))
                    subgroups[possibilitiesKey].add(cell)
            # Instead of applying directly consider first listing the possibilities independently
            # so keeping a structure of group key, subgroup cells, valueset then applying those later
            for k in subgroups.keys():
                if len(subgroupPossibilities[k]) == len(subgroups[k]) and len(subgroups[k]) > 1:
                    for cell in agroup["cells"] - subgroups[k]:
                        if cell in self.emptycells:
                            self.updateCandidates(cell, "perfect subgroups",
                                                  "{0} subgroup {1}: {2}".format(agroup["name"], self.cellstostr(subgroups[k]), str(sorted(subgroupPossibilities[k]))),
                                                  subgroupPossibilities[k])


    # Filters by looking for subgroups of values inside a group, where a subgroup
    # of size N exists in N cells (with N > 1 and N < 9) - which means that the
    # values of this subgroup can be eliminated from the other cells in the group.
    # This is similar to the above method however does not require the subgroups are
    # complete, i.e. there could be two cells with possibilities {1,6,7} and {1,3,7,8}
    # and {1,7} not occuring anywhere else in the possibilities of that group. This
    # means the two cells can be limited to just {1,7} and both 1 and 7 can be
    # eliminated from the rest of the group.
    def subgroupElimination(self):
        for groupPair in self.overlappingGroups:
            print(groupPair)
            print(groupPair[0])
            print(self.groups[groupPair[0]])
            overlap = self.groups[groupPair[0]]["cells"].intersection(self.groups[groupPair[1]]["cells"])
            possibilitiesInOverlap = set()
            for cell in overlap:
                if cell in self.emptycells:
                    possibilitiesInOverlap.add(self.possibilities[cell])
            if len(possibilitiesInOverlap)>0:
                print("Overlap {0} and {1} has {2}".format(self.groups[groupPair[0]]["name"], self.groups[groupPair[1]]["name"], str(overlap)))
            valuesInOverlap = None
            valuesInRestOf1 = None
            valuesInRestOf2 = None


    # Filters by looking at intersections of pairs of groups. If a value can only occur
    # in that intersection from the perspective of one of the two groups, that value can
    # be eliminated from the rest of the other group as well.
    def radiationElimination(self):
        pass

    def batchSolve(self):
        n = 0
        while not self.isCompleted():
            n = n + 1
            self.groupElimination()
            self.perfectSubgroupElimination()
            mvz = self.getMoves()
            if len(mvz) == 0:
                print("No moves!")
                break
            for mv in sorted(mvz.keys()):
                self.place(mvz[mv]["move"], self.celltostr(mv))
        return n

class NRCSudoku(Sudoku):
    """ Adds rectangular areas """

    def initGroups(self):
        super().initGroups()
        r1 = set()
        r2 = set()
        r3 = set()
        r4 = set()
        for i in range(9):
            for j in range(9):
                if (i >= 1 and i <= 3 and j >= 1 and j <= 3):
                    r1.add((i, j))
                if (i >= 1 and i <= 3 and j >= 5 and j <= 7):
                    r2.add((i, j))
                if (i >= 5 and i <= 7 and j >= 1 and j <= 3):
                    r3.add((i, j))
                if (i >= 5 and i <= 7 and j >= 5 and j <= 7):
                    r4.add((i, j))
        self.groups.append({"name": "nrc 1", "cells": r1})
        self.groups.append({"name": "nrc 2", "cells": r2})
        self.groups.append({"name": "nrc 3", "cells": r3})
        self.groups.append({"name": "nrc 4", "cells": r4})

    def getShowRaster(self):
        mx = super().getShowRaster()
        for x in range(0, 3):
            for y in range(0, 3):
                mx[x + 1, y + 1] = 2
                mx[x + 5, y + 1] = 2
                mx[x + 1, y + 5] = 2
                mx[x + 5, y + 5] = 2
        return mx

def main():
    # https://www.nrc.nl/nieuws/2018/02/03/sudoku-a1590454
    # NRC saturday 3 feb 2018
    # solvable by simple elimination only :(
    s = NRCSudoku((" 9   4 7 ",
                   " 7 3  9 8",
                   "         ",
                   "      5  ",
                   "   8     ",
                   "         ",
                   "5    6  9",
                   " 3  41   ",
                   "    7    ")
                  )

    # NRC saturday 29 feb 2020
    # even this one requires nothing fancy
    s1 = NRCSudoku((" 1   2   ",
                    "  8      ",
                    "      5 3",
                    "   9    2",
                    "       9 ",
                    "4 52     ",
                    "    1 38 ",
                    "         ",
                    "  6      "))
    s.print()

    print("Batch solving")
    s_copy = copy.deepcopy(s)
    nmoves = s_copy.batchSolve()
    print( "Solved in {0} steps".format(nmoves))
    print(s_copy.eliminationSteps)


    while not s.isCompleted():
        s.groupElimination()
        sbefore = copy.deepcopy(s)
        s.perfectSubgroupElimination()
        s.subgroupElimination()
        mvz = s.getMoves()
        if len(mvz) == 0:
            print("No moves!")
            break
        for mv in sorted(mvz.keys()):
            print("Possible move {0} at {1}".format(mvz[mv]["move"], s.celltostr(mv)))
            for r in mvz[mv]["reasons"]:
                print("   explanation: " + r["method"])
                for detail in r["reason"]:
                    print("      * " + str(detail))
        sbefore.show()
        nextMove = sorted(mvz.keys())[0]
        s.place(mvz[nextMove]["move"], s.celltostr(nextMove))


if __name__ == "__main__":
    main()

# TODO add mode to batch-solve puzzle and report on # of steps
# also check consistency while doing that
