"""
.. module:: CreateIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
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
#import IndexSplitter

maxRAMused = (psutil.Process(os.getpid())).memory_info().rss


def main(argv):
    """
    Main script for all of the discipline's assignments. This script is responsable for calling the correct classes and for creating the data flow necessary for the index to be created and persisted.

    :param argv: receives the arguments passed to the program during execution
    :type argv: list<str>

    """

    HELP = """USAGE:\n
    python3 CreateIndex.py [-h] [-p] [-w] [-o outputFolder] [-l limit] [-t tokenizer] [-r limitRAM] inputFolder\n
        OPTIONS:
           h - shows this help
           o - define output file's folder
           l - define limit for the number of lines to be processed in each input file
           t - define the tokenizer used for the program
           r - limit program execution to defined RAM capacity
           w - process weights of terms
           p - process positions of terms
        ARGUMENTS:
           outputFolder - actual name for the output folder
           limit - value for the number of lines limit
           tokenizer - must be simple(for the simple 2.1 tokenizer) or complex(for the more advanced 2.2 tokenizer)
           limitRAM - maximum RAM(in Gb) used in the indexing process
           inputFolder - name of the folder that contains the input files to be processed"""

    # default variables
    outputFolder = "index"
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

    if args == [] or len(args) != 1:
        print(HELP)
        return 2

    # verifies if any option was passed to the script
    for opt, arg in opts:
        if opt == '-h':
            print(HELP)
            return 3
        elif opt == "-o":
            outputFolder = arg
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
                        outputFolder, args[0], limit, weightCalc, positionCalc)
        else:
            assignment2(Tokenizer.SimpleTokenizer(), outputFolder,
                        args[0], limit, weightCalc, positionCalc, maximumRAM)

    else:  # 'complex' = default tokenizer
        if maximumRAM is None:
            assignment1(Tokenizer.ComplexTokenizer(),
                        outputFolder, args[0], limit, weightCalc, positionCalc)
        else:
            assignment2(Tokenizer.ComplexTokenizer(), outputFolder,
                        args[0], limit, weightCalc, positionCalc, maximumRAM)

    return 0


def assignment1(tokenizer, outputFolder, inputFolder, limit, weightCalc, positionCalc):
    """
    Follows the execution flow specific for the first assignment.

    :param tokenizer: class instance to be used in the tokenization process
    :type tokenizer: Tokenizer
    :param outputFolder: name of the folder where the final index will be written to
    :type outputFolder: str
    :param inputFiles: list of the names of the files containing the textual information to be indexed
    :type inputFiles: list<str>
    :param limit: limit number of documents to have in consideration, None if no limit
    :type limit: int
    :param weightCalc: True if the term weights are to be calculated, False if not
    :type weightCalc: bool
    :param positionCalc: True if the term positions are to be calculated, False if not
    :type positionCalc: bool

    """

    parser = FileParser.GZipFileParser(inputFolder, limit)
    indexer = Indexer.FileIndexer(tokenizer, positionCalc, parser)
    if weightCalc and positionCalc:
        persister = PersistIndex.PersistCSVWeightedPosition(
            outputFolder, indexer, parser.docID)
        persister.persist()
    elif weightCalc:
        persister = PersistIndex.PersistCSVWeighted(
            outputFolder, indexer, parser.docID)
        persister.persist()
    elif positionCalc:
        persister = PersistIndex.PersistCSVPosition(
            outputFolder, indexer, parser.docID)
        persister.persist()
    else:
        persister = PersistIndex.PersistCSV(
            outputFolder, indexer, parser.docID)
        persister.persist()

    tokenizer.clearVar()
    parser.clearVar()
    indexer.clearVar()
    persister.clearVar()
    del parser
    del indexer
    del tokenizer
    del persister
    gc.collect()


def assignment2(tokenizer, outputFolder, inputFolder, limit, weightCalc, positionCalc, maximumRAM):
    """
    Follows the execution flow specific for the second assignment.

    :param tokenizer: class instance to be used in the tokenization process
    :type tokenizer: Tokenizer
    :param outputFolder: name of the folder where the final index will be written to
    :type outputFolder: str
    :param inputFolder: list of one element representing the name of the folder that contains the files with the textual information to be indexed
    :type inputFolder: list<str>
    :param limit: limit number of documents to have in consideration, None if no limit
    :type limit: int
    :param weightCalc: True if the term weights are to be calculated, False if not
    :type weightCalc: bool
    :param positionCalc: True if the term positions are to be calculated, False if not
    :type positionCalc: bool
    :param maximumRAM: maximum amount of RAM (in Gb) allowed for the program execution
    :type maximumRAM: int

    """

    parser = FileParser.LimitedRamFileParser(inputFolder, limit)

    indexer = Indexer.FileIndexer(tokenizer, positionCalc)
    if weightCalc and positionCalc:
        persister = PersistIndex.PersistCSVWeightedPosition(
            outputFolder, indexer)
    elif weightCalc:
        persister = PersistIndex.PersistCSVWeighted(outputFolder, indexer)
    elif positionCalc:
        persister = PersistIndex.PersistCSVPosition(outputFolder, indexer)
    else:
        persister = PersistIndex.PersistCSV(outputFolder, indexer)

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
            persister.setTotalNumDocs(parser.docID)
            persister.persist(indexer.index)
            return 0
        else:
            persister.setTotalNumDocs(parser.docID)
            if persister.persist(indexer.index, auxFile.format(blockCounter)):
                blockCounter += 1
        indexer.clearVar()
        persister.clearVar()
        tokenizer.clearTokens()
        gc.collect()

    if weightCalc and positionCalc:
        merger = Merger.PositionWeightMerger(
            [auxFile.format(x) for x in range(1, blockCounter)], parser.docID, outputFolder)
    elif weightCalc:
        merger = Merger.WeightMerger(
            [auxFile.format(x) for x in range(1, blockCounter)], parser.docID, outputFolder)
    elif positionCalc:
        merger = Merger.PositionMerger(
            [auxFile.format(x) for x in range(1, blockCounter)], parser.docID, outputFolder)
    else:
        merger = Merger.SimpleMerger(
            [auxFile.format(x) for x in range(1, blockCounter)], parser.docID, outputFolder)

    # merging intermediateIndexes
    tokenizer.clearVar()
    parser.clearVar()
    indexer.clearVar()
    persister.clearVar()
    del parser
    del tokenizer
    del persister

    runSPIMI = True
    allDone = False
    print("Merging...")
    while(runSPIMI):
        while not allDone and isMemoryAvailable(maximumRAM):
            allDone = merger.mergeIndex()
            if allDone:
                runSPIMI = False
                merger.writeIndex()
                break
        merger.writeIndex()
        gc.collect()

    del merger


def isMemoryAvailable(maximumRAM):
    """
    Auxiliary function used to determine whether there is still memory available to keep reading information from the input files or not.

    :param maximumRAM: maximum amount of RAM (in Gb) allowed for the program execution
    :type maximumRAM: int
    :returns: True if the memory usage is under 85% of the maximum RAM allowed, false if not
    :rtype: bool

    """
    # pass this verification because if it's to much it's user error
    # if psutil.virtual_memory().percent > 98:  # we avoid using 100% of memory as a prevention measure
    #     return False

    # get program memory usage
    processMemory = process.memory_info().rss
    # print(processMemory)
    if processMemory >= int(maximumRAM*0.9):
        return False

    return True


if __name__ == "__main__":
    # bypassing the script arguments to the main function
    process = psutil.Process(os.getpid())
    main(sys.argv[1:])
