
# Authors: Filipe Pires [85122] & João Alegria [85048]

import sys

from FileParser import FileParser
import Tokenizer
import PersistIndex

# Main class for Project 1

def main(args):

    HELP = """USAGE:\n
           python3 Indexer.py [-h] [-o outputFile] [-l limit] inputFile1 [inputFile2]+ \n
        OPTIONS:\n
           h - shows this help\n
           o - define output file's name\n
           l - define limit for the number of lines to be processed in each input file\n
        ARGUMENTS:\n
           outputFile - actual name for the output file\n
           limit - value for the number of lines limit\n
           inputFile - names of the input files to be processed\n"""

    ERROR = "Please execute this command with the correct argument(s) or add the option '-h' to learn about its usage.\n"

    if len(args) < 1:
        print(ERROR)
        return 0
        
    for i in range(0,len(args)-1):
        if args[i] == "-h" or args[i] == "-help" or args[i] == "--help":
            print(HELP)
            return 0

    inputFiles = args.copy()
    outputFile = "out.txt"
    limit = None

    for i in range(0,len(args)-1):
        if args[i] == "-o":
            assert not args[i+1].startswith("-")
            outputFile = args[i+1]
            inputFiles.remove(args[i])
            inputFiles.remove(args[i+1])
        if args[i] == "-l":
            assert not args[i+1].startswith("-")
            limit = int(args[i+1])
            inputFiles.remove(args[i])
            inputFiles.remove(args[i+1])

    #fp = FileParser(["2004_TREC_ASCII_MEDLINE_1"], 300)
    #fp = FileParser(["test.txt"], 300)
    fp = FileParser(inputFiles, limit)
    fp.getContent()
    t = Tokenizer.SimpleTokenizer(fp.content)
    print(fp.content)
    t.tokenize()
    PersistIndex.PersistCSV(t.tokens, outputFile).persist()
    return 0

main(sys.argv[1:])