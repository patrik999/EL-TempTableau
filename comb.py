#!/usr/bin/env python

import getopt, sys
import optparse
import time

from util_mm import createClauseList, createModelList
from min_model_gen import MinModelGenerator
from tableau import TableauGenerator

def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('--file', action="store", dest="file", default="")
    parser.add_option('--mode', action="store", dest="mode", default=2)
    parser.add_option('--top', action="store", dest="top", default="")
    parser.add_option('--reduct', action="store_true", dest="reduct", default=False)
    parser.add_option('--print', action="store_true", dest="printTrace", default=False)
    (options, args) = parser.parse_args()

    file1 = open(options.file, 'r')
    lines = file1.readlines()
    file1.close()

    print("Mode: " + str(options.mode))
    print("Reduct: " + str(options.reduct))

    clauseList1 = createClauseList(lines, {})
    clauseList2 = createClauseList(lines, {}) # Need a second one to have a original copy

    print("Clauses in CNF: " + str(clauseList1))

    # Main
    tabGen = TableauGenerator(clauseList1,  {},  options.top, int(options.mode), False) # For now temp mode off
    models = tabGen.solve(options.printTrace)

    for model in models:

        print("Active model: " + str(model))

        modelList =  []
        modelListRaw = model # []
        #createModelList(model, modelList, modelListRaw)
        for i in range(len(modelListRaw)):
            modelList.append("a:" + str(modelListRaw[i]))

        modelGen = MinModelGenerator(clauseList2, modelList,  int(options.mode), False) # True
        modelGen.analyze(options.reduct, modelListRaw)

        isMinimal = modelGen.solve(options.reduct)

        if (isMinimal):
            print("Model is minimal")
        else:
            print("Model is not minimal")

        #break


    print("Finished")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])