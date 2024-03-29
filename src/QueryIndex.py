"""
.. module:: QueryIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""

import os
import sys
import psutil
import gc
import time
import getopt

import Tokenizer
import Searcher

maxRAMused = (psutil.Process(os.getpid())).memory_info().rss


def main(argv):
    """
    Main script for the discipline's assignment 3. This script is responsable for calling the correct classes and for creating the data flow necessary for querying an existing index.

    :param argv: receives the arguments passed to the program during execution
    :type argv: list<str>

    """

    HELP = """USAGE:\n
    python3 QueryIndex.py [-h] [-o outputFile] [-t tokenizer] [-r limitRAM] [-f feedback] [-s rocchioScope] [-c numChamps] [-l limit] <queryFile> <indexFolder> [a b g] \n
        OPTIONS:
           h - shows this help
           f - tells 
           o - define output file's name
           t - define the tokenizer used for the program
           r - limit program execution to defined RAM capacity
           f - define the feedback used for the Rocchio algorithm
           s - define the number of retrieved documents considered for the Rocchio algorithm
           c - define the size of the champions list
           l - define the number of scores to return
        ARGUMENTS:
           outputFile - actual name for the output file
           tokenizer - must be 'simple' or 'complex' 
           limitRAM - maximum RAM(in Gb) used in the indexing process
           queryFile - name of the file containing 1 or more queries
           indexFolder - name of the folder that contains the indexes
           a - alpha weight for the Rocchio algorithm
           b - beta weight for the Rocchio algorithm
           g - gamma weight for the Rocchio algorithm
           feedback - must be 'user' or 'pseudo'
           rocchioScope - number of retrieved documents considered for the Rocchio algorithm
           numChamps - size of the champions list
           limit - limit number of scores to return"""

    # default variables
    outputFile = "../queryResults/"
    tokenizer = "complex"
    maximumRAM = None
    feedback = None             # None, pseudo or user
    rocchioWeights = []         # alpha, beta and gamma
    n = None                    # number of relevant docs (for feedback)
    k = 10000                   # champions list size
    limit = 100                 # number of scores

    try:
        opts, args = getopt.getopt(argv, "ho:t:r:f:c:s:l:")
    except getopt.GetoptError:
        print(HELP)
        return 1

    if args == [] or (len(args) != 2 and len(args) != 4 and len(args) != 5):
        print(HELP)
        return 2

    # verifies if any option was passed to the script
    for opt, arg in opts:
        if opt == '-h':
            print(HELP)
            return 3
        elif opt == "-o":
            outputFile = arg
        elif opt == "-t":
            assert arg in (
                "simple", "complex"), "Tokenizer option must be either \"simple\" or \"complex\"."
            tokenizer = arg
        elif opt == "-r":
            maxM = psutil.virtual_memory().free
            if arg != "":
                maximumRAM = float(arg)*1000000000
            else:
                maximumRAM = maxM
            if maximumRAM > maxM:
                maximumRAM = maxM
                print("Warning: Memory available is less than the asked value, maximumRAM set to " +
                      str(int(maximumRAM/1000000000)) + "Gb.")
        elif opt == "-f":
            assert arg in (
                "user", "pseudo"), "Feedback option must be either \"user\" or \"pseudo\"."
            feedback = arg
        elif opt == "-c":
            assert int(
                arg) > 0, "Error: numChamps value must be a positive integer"
            k = int(arg)
        elif opt == "-s":
            assert int(
                arg) > 0, "Error: rocchioScope value must be a positive integer"
            n = int(arg)
        elif opt == "-l":
            assert int(arg) > 0, "Error: limit value must be a positive integer"
            limit = int(arg)

    if feedback:
        if feedback == "pseudo":
            assert len(
                args) == 4, "Error: if you want to use pseudo feedback, please insert alpha and beta as well"
            rocchioWeights.append(float(args[2]))
            rocchioWeights.append(float(args[3]))
            # rocchioWeights.append(float(args[4]))
        else:
            assert len(
                args) == 5, "Error: if you want to use user feedback, please insert alpha, beta and gamma as well"
            rocchioWeights.append(float(args[2]))
            rocchioWeights.append(float(args[3]))
            rocchioWeights.append(float(args[4]))

    # taking in account the choosen tokenizer, the respective data flow is created
    if tokenizer == "simple":
        assignment3(outputFile, Tokenizer.SimpleTokenizer(
        ), maximumRAM, feedback, n, k, limit, args[0], args[1], rocchioWeights)
    else:  # 'complex' = default tokenizer
        assignment3(outputFile, Tokenizer.ComplexTokenizer(
        ), maximumRAM, feedback, n, k, limit, args[0], args[1], rocchioWeights)

    return 0


def assignment3(outputFile, tokenizer, maximumRAM, feedback, rocchioScope, numChamps, limit, queryFile, inputFolder, rocchioWeights):
    """
    Follows the execution flow specific for the third assignment.

    :param outputFile: name of the file where the query results will be written to
    :type outputFile: str
    :param tokenizer: class instance to be used in the tokenization process
    :type tokenizer: Tokenizer
    :param maximumRAM: maximum amount of RAM (in Gb) allowed for the program execution
    :type maximumRAM: int
    :param feedback: type of feedback used in the rocchio algorithm
    :type feedback: str
    :param rocchioScope: number of retrieved documents considered for the Rocchio algorithm
    :type rocchioScope: int
    :param numChamps: size of the champions list
    :type numChamps: int
    :param limit: number of Scores to return
    :type limit: int
    :param queryFile: name of the file where the query (or queries) are written
    :type queryFile: str
    :param inputFolder: list of one element representing the name of the folder that contains the indexes
    :type inputFolder: list<str>
    :param rocchioWeights: list of weights used in the rocchio algorithm
    :type rocchioWeights: list<float>
    """

    searcher = Searcher.IndexSearcher(
        tokenizer, limit, inputFolder, maximumRAM, feedback, rocchioScope, numChamps, rocchioWeights)

    f = open(queryFile, "r")
    for line in f:  # for each query
        content = line.split("\t")

        # retrieve required index files
        searcher.retrieveRequiredFiles("".join(x for x in content[1:]))

        # calculate the score of each document
        if feedback:
            searcher.calculateScores(int(content[0]))
        else:
            searcher.calculateScores()

        # sort results and write them
        searcher.sortAndWriteResults(outputFile+content[0])
        # exit(0)
    return


if __name__ == "__main__":
    # bypassing the script arguments to the main function
    main(sys.argv[1:])
