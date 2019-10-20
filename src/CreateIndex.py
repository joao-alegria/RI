"""
.. module:: CreateIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""

import os
import sys
import psutil
import gc

import FileParser
import Tokenizer
import PersistIndex
import Indexer


def main(args):
    """
    Main script for Project 1. This script is responsable for calling the correct classes and for creating the data flow necessary for the index to be created and persisted.

    :param args: receives the arguments passed to the program during execution
    :type args: list<str>

    """

    HELP = """USAGE:\n
           python3 CreateIndex.py [-h] [-o outputFile] [-l limit] [-t tokenizer] [-r limitRAM] inputFile1 [inputFile2]+ \n
        OPTIONS:\n
           h - shows this help\n
           o - define output file's name\n
           l - define limit for the number of lines to be processed in each input file\n
           t - define the tokenizer used for the program\n
           r - limit program execution to defined RAM capacity\n
        ARGUMENTS:\n
           outputFile - actual name for the output file\n
           limit - value for the number of lines limit\n
           tokenizer - must be simple(for the simple 2.1 tokenizer) or complex(for the more advanced 2.2 tokenizer)\n
           limitRAM - maximum RAM used in the indexing process (if equals to 0, the program uses the maximum RAM capacity available)\n
           inputFile - names of the input files to be processed\n"""

    ERROR = "Please execute this command with the correct argument(s) or add the option '-h' to learn about its usage.\n"

    if len(args) < 1:
        print(HELP)
        return 1

    for i in range(0, len(args)-1):
        if args[i] == "-h" or args[i] == "-help" or args[i] == "--help":
            print(HELP)
            return 2

    # default variables
    inputFiles = args.copy()
    outputFile = "out.txt"
    limit = None
    tokenizer = "simple"
    maximumRAM = None

    # verifies if any option was passed to the script
    for i in range(0, len(args)-1):
        if args[i] == "-o":
            assert not args[i +
                            1].startswith("-"), "This option must have the value indicated."
            outputFile = args[i+1]
            inputFiles.remove(args[i])
            inputFiles.remove(args[i+1])
        if args[i] == "-l":
            assert not args[i +
                            1].startswith("-"), "This option must have the value indicated."
            limit = int(args[i+1])
            inputFiles.remove(args[i])
            inputFiles.remove(args[i+1])
        if args[i] == "-t":
            assert not args[i +
                            1].startswith("-"), "This option must have the value indicated."
            assert args[i+1] == "simple" or args[i +
                                                 1] == "complex", "Tokenizer option must be either \"simple\" or \"complex\"."
            tokenizer = args[i+1]
            inputFiles.remove(args[i])
            inputFiles.remove(args[i+1])
        if args[i] == "-r":
            assert not args[i +
                            1].startswith("-"), "This option must have the value indicated."
            assert float(args[i+1]
                         ) >= 0, "RAM capacity value must be an integer larger or equal to zero."
            maximumRAM = float(args[i+1])*1000000000
            print(maximumRAM)
            print(psutil.virtual_memory().free)
            if maximumRAM > psutil.virtual_memory().free:
                maximumRAM = psutil.virtual_memory().free
                print("Warning: Memory available is less than the asked value, maximumRAM set to " +
                      str(int(maximumRAM/1000000000)) + "Gb.")
            inputFiles.remove(args[i])
            inputFiles.remove(args[i+1])

    # taking in account the choosen tokenizer, the respective data flow is created
    if tokenizer == "simple":
        if maximumRAM is None:
            assignment1(Tokenizer.SimpleTokenizer(),
                        outputFile, inputFiles, limit)
        else:
            assignment2(Tokenizer.SimpleTokenizer(), outputFile,
                        inputFiles, limit, maximumRAM)

    else:  # 'complex' = default tokenizer
        if maximumRAM is None:
            assignment1(Tokenizer.ComplexTokenizer(),
                        outputFile, inputFiles, limit)
        else:
            assignment2(Tokenizer.ComplexTokenizer(), outputFile,
                        inputFiles, limit, maximumRAM)
    return 0


def assignment1(tokenizer, outputFile, inputFiles, limit):
    PersistIndex.PersistCSV(
        outputFile,
        indexer=Indexer.FileIndexer(
            tokenizer,
            FileParser.GZipFileParser(inputFiles, limit)
        )
    ).persist()


def assignment2(tokenizer, outputFile, inputFiles, limit, maximumRAM):
    parser = FileParser.LimitedRamFileParser(inputFiles, limit)

    # Indexer is not always the same!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    indexer = Indexer.WeightedFilePositionIndexer(tokenizer)
    # Persistor is not always the same!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    persister = PersistIndex.PersistCSVWeightedPosition(outputFile)
    auxFile = "intermediate_index_{0}.txt"
    blockCounter = 1

    # fazer getContent() no NewFileParser retorna so 1 documento
    runSPIMI = True
    while(runSPIMI):

        while(isMemoryAvailable(maximumRAM)):
            doc = parser.getContent()
            if not doc:
                runSPIMI = False
                break
            indexer.createIndex(doc)

        indexer.normalizeIndex
        if persister.persist(
            # ver as posiçoes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                (indexer.index, indexer.positionIndex), auxFile.format(blockCounter)):
            blockCounter += 1
        indexer.clearVar()
        gc.collect()
    # fazer mergeIndex() no NewPersist
    persister.mergeIndex([auxFile.format(x) for x in range(1, blockCounter)])


process = psutil.Process(os.getpid())


def isMemoryAvailable(maximumRAM):
    # pass this verification because if it's to much its user error
    # if psutil.virtual_memory().percent > 98:  # we avoid using 100% of memory as a prevention measure
    #     return False

    # get memory being used by program
    processMemory = process.memory_info().rss
    print(processMemory)
    if processMemory >= maximumRAM:
        return False

    return True


if __name__ == "__main__":
    # bypassing the script arguments to the main function
    main(sys.argv[1:])
