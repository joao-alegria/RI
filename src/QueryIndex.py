"""
.. module:: QueryIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""

import os
import sys
import psutil
import gc
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
    python3 QueryIndex.py [-h] [-p] [-o outputFile] [-t tokenizer] [-r limitRAM] [-f feedback] [-k k] queryFile indexFolder [a b g] \n
        OPTIONS:
           h - shows this help
           p - tells if indexes have positions calculated
           f - tells 
           o - define output file's name
           t - define the tokenizer used for the program
           r - limit program execution to defined RAM capacity
           f - define the feedback used for the Rocchio algorithm
           k - define the number of retrieved documents considered for the Rocchio algorithm
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
           k - number of retrieved documents considered for the Rocchio algorithm"""

    # default variables
    outputFile = "../queryResults/results"
    positionCalc = False
    tokenizer = "simple"
    maximumRAM = None
    feedback = None
    rocchioWeights = []
    k = 10

    try:
        opts, args = getopt.getopt(argv, "hpo:t:r:f:k:")
    except getopt.GetoptError:
        print(HELP)
        return 1

    if args == [] or (len(args) != 2 and len(args) != 5):
        print(HELP)
        return 2

    # verifies if any option was passed to the script
    for opt, arg in opts:
        if opt == '-h':
            print(HELP)
            return 3
        elif opt == "-o":
            outputFile = arg
        elif opt == "-p":
            positionCalc = True
        elif opt == "-t":
            assert arg in ("simple", "complex"), "Tokenizer option must be either \"simple\" or \"complex\"."
            tokenizer = arg
        elif opt == "-r":
            maxM = psutil.virtual_memory().free
            if arg != "":
                maximumRAM = float(arg)*1000000000
            else:
                maximumRAM = maxM
            if maximumRAM > maxM:
                maximumRAM = maxM
                print("Warning: Memory available is less than the asked value, maximumRAM set to " + str(int(maximumRAM/1000000000)) + "Gb.")
        elif opt == "-f":
            assert arg in ("user", "pseudo"), "Feedback option must be either \"user\" or \"pseudo\"."
            feedback = arg
        elif opt == "-k":
            assert int(arg) > 0, "Error: k value must be a positive integer"
            k = int(arg)

    if feedback:
        if len(args) >= 5:
            rocchioWeights.append(float(args[2]))
            rocchioWeights.append(float(args[3]))
            rocchioWeights.append(float(args[4]))
        else:
            rocchioWeights.append(1.0)
            rocchioWeights.append(0.5)
            rocchioWeights.append(0.25)
        rocchioWeights.append(k)

    # taking in account the choosen tokenizer, the respective data flow is created
    if tokenizer == "simple":
        assignment3(Tokenizer.SimpleTokenizer(), outputFile, args[0], args[1], positionCalc, feedback, rocchioWeights, maximumRAM)
    else:  # 'complex' = default tokenizer
        assignment3(Tokenizer.ComplexTokenizer(), outputFile, args[0], args[1], positionCalc, feedback, rocchioWeights, maximumRAM)

    return 0


def assignment3(tokenizer, outputFile, queryFile, inputFolder, positionCalc, feedback, rocchioWeights, maximumRAM):
    """
    Follows the execution flow specific for the third assignment.

    :param tokenizer: class instance to be used in the tokenization process
    :type tokenizer: Tokenizer
    :param outputFile: name of the file where the query results will be written to
    :type outputFile: str
    :param queryFile: name of the file where the query (or queries) are written
    :type queryFile: str
    :param inputFolder: list of one element representing the name of the folder that contains the indexes
    :type inputFolder: list<str>
    :param positionCalc: True if the term positions are to be calculated, False if not
    :type positionCalc: bool
    :param feedback: type of feedback used in the rocchio algorithm
    :type feedback: str
    :param rocchioWeights: list of weights used in the rocchio algorithm
    :type rocchioWeights: list<float>
    :param maximumRAM: maximum amount of RAM (in Gb) allowed for the program execution
    :type maximumRAM: int

    """

    searcher = Searcher.IndexSearcher(inputFolder, tokenizer, positionCalc, feedback, rocchioWeights, maximumRAM)

    f = open(queryFile,"r")
    for line in f:
        content = line.split("\t")
        searcher.processQuery(content[-1],outputFile+"_"+content[0])
    return

if __name__ == "__main__":
    # bypassing the script arguments to the main function
    process = psutil.Process(os.getpid())
    main(sys.argv[1:])
