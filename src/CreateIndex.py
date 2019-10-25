"""
.. module:: CreateIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""

import os
import sys
import psutil
import gc
import getopt

import FileParser
import Tokenizer
import PersistIndex
import Indexer
import Merger

maxRAMused = (psutil.Process(os.getpid())).memory_info().rss

def main(argv):
    """
    Main script for Project 1. This script is responsable for calling the correct classes and for creating the data flow necessary for the index to be created and persisted.

    :param args: receives the arguments passed to the program during execution
    :type args: list<str>

    """

    HELP = """USAGE:\n
    python3 CreateIndex.py [-h] [-o outputFile] [-l limit] [-t tokenizer] [-r limitRAM] inputFile1 [inputFile2]+\n
        OPTIONS:
           h - shows this help
           o - define output file's name
           l - define limit for the number of lines to be processed in each input file
           t - define the tokenizer used for the program
           r - limit program execution to defined RAM capacity
           w - process weights of terms
           p - process positions of terms
        ARGUMENTS:
           outputFile - actual name for the output file
           limit - value for the number of lines limit
           tokenizer - must be simple(for the simple 2.1 tokenizer) or complex(for the more advanced 2.2 tokenizer)
           limitRAM - maximum RAM used in the indexing process (if equals to 0, the program uses the maximum RAM capacity available)
           inputFile - names of the input files to be processed"""

    # default variables
    outputFile = "out.txt"
    limit = None
    tokenizer = "simple"
    maximumRAM = None
    weightCalc = False
    positionCalc = False

    try:
        opts, args = getopt.getopt(argv, "wpho:t:l:r:")
    except getopt.GetoptError:
        print(HELP)
        return 1

    if args == []:
        print(HELP)
        return 2

    # verifies if any option was passed to the script
    for opt, arg in opts:
        if opt == '-h':
            print(HELP)
            return 3
        elif opt == "-o":
            outputFile = arg
        elif opt == "-l":
            limit = int(arg)
        elif opt == "-t":
            assert arg in (
                "simple", "complex"), "Tokenizer option must be either \"simple\" or \"complex\"."
            tokenizer = arg
        elif opt == "-w":
            weightCalc = True
        elif opt == "-p":
            positionCalc = True
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

    # taking in account the choosen tokenizer, the respective data flow is created
    if tokenizer == "simple":
        if maximumRAM is None:
            assignment1(Tokenizer.SimpleTokenizer(),
                        outputFile, args, limit, weightCalc, positionCalc)
        else:
            assignment2(Tokenizer.SimpleTokenizer(), outputFile,
                        args, limit, weightCalc, positionCalc, maximumRAM)

    else:  # 'complex' = default tokenizer
        if maximumRAM is None:
            assignment1(Tokenizer.ComplexTokenizer(),
                        outputFile, args, limit, weightCalc, positionCalc)
        else:
            assignment2(Tokenizer.ComplexTokenizer(), outputFile,
                        args, limit, weightCalc, positionCalc, maximumRAM)
    return 0


def assignment1(tokenizer, outputFile, inputFiles, limit, weightCalc, positionCalc):
    fileParser = FileParser.GZipFileParser(inputFiles, limit)
    indexer = Indexer.WeightedFileIndexer(
        tokenizer, fileParser) if weightCalc else Indexer.FileIndexer(tokenizer, fileParser)
    if weightCalc and positionCalc:
        PersistIndex.PersistCSVWeightedPosition(outputFile, indexer).persist()
    elif weightCalc:
        PersistIndex.PersistCSVWeighted(outputFile, indexer).persist()
    elif positionCalc:
        PersistIndex.PersistCSVPosition(outputFile, indexer).persist()
    else:
        PersistIndex.PersistCSV(outputFile, indexer).persist()


def assignment2(tokenizer, outputFile, inputFiles, limit, weightCalc, positionCalc, maximumRAM):
    parser = FileParser.LimitedRamFileParser(inputFiles, limit)

    indexer = Indexer.WeightedFileIndexer(
        tokenizer) if weightCalc else Indexer.FileIndexer(tokenizer)
    if weightCalc and positionCalc:
        persister = PersistIndex.PersistCSVWeightedPosition(outputFile)
    elif weightCalc:
        persister = PersistIndex.PersistCSVWeighted(outputFile)
    elif positionCalc:
        persister = PersistIndex.PersistCSVPosition(outputFile)
    else:
        persister = PersistIndex.PersistCSV(outputFile)

    auxFile = "intermediate_index_{0}.txt"
    blockCounter = 1

    # getContent() in this context(with LimitedParser) returns 1 document
    runSPIMI = True
    while(runSPIMI):

        while(isMemoryAvailable(maximumRAM)):
            doc = parser.getContent()
            if not doc:
                runSPIMI = False
                break
            indexer.createIndex(doc)

        # TODO: when writing ram usage jumps up
        if not runSPIMI and blockCounter == 1:
            persister.persist(indexer.normalizeIndex())
            return 0
        else:
            if persister.persist((indexer.index,indexer.positionIndex), auxFile.format(blockCounter)):
                blockCounter += 1
        indexer.clearVar()
        gc.collect()

    # merging intermidiateIndexes
    del parser
    del indexer
    del tokenizer
    del persister
    gc.collect()

    merger = Merger.Merger(
        outputFile, [auxFile.format(x) for x in range(1, blockCounter)])
    runSPIMI = True
    allDone = False
    while(runSPIMI):
        while not allDone and isMemoryAvailable(maximumRAM):
            allDone = merger.mergeIndex()
            if allDone:
                runSPIMI = False
                break
        print("writing")

        merger.writeIndex()
        gc.collect()

    return 0


def isMemoryAvailable(maximumRAM):
    # pass this verification because if it's to much it's user error
    # if psutil.virtual_memory().percent > 98:  # we avoid using 100% of memory as a prevention measure
    #     return False

    # get program memory usage
    processMemory = process.memory_info().rss
    print(processMemory)
    if processMemory >= maximumRAM:
        return False

    return True


if __name__ == "__main__":
    # bypassing the script arguments to the main function
    process = psutil.Process(os.getpid())
    main(sys.argv[1:])
