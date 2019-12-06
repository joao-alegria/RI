"""
.. module:: Searcher
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""

import os
import math
from abc import ABC, abstractmethod


class Searcher(ABC):
    """
    Abstract class that serves as template and interface for future instances and implementations.

    :param inputFolder: name of the folder containing the files to be used as input
    :type inputFolder: str
    :param tokenizer: instance of the tokenizer used in the context to process the content of the corpus
    :type tokenizer: Tokenizer
    :param maximumRAM: maximum amount of RAM (in Gb) allowed for the program execution
    :type maximumRAM: int

    """

    def __init__(self, inputFolder, tokenizer, positionCalc, feedback=None, rocchioWeights=[], maximumRAM=None):
        """
        Class constructor
        """
        super().__init__()

        self.files = []
        self.inputFolder = inputFolder+"/"
        inputFiles = os.listdir(inputFolder)
        for f in inputFiles:
            self.files.append(f)
        self.tokenizer = tokenizer
        self.positionCalc = positionCalc
        self.feedback = feedback
        self.rocchioWeights = rocchioWeights
        self.maximumRAM = maximumRAM
        translationFile = open("../indexMetadata.txt")
        self.translations = {}
        for line in translationFile:
            line = line.strip().split(",")
            self.translations[line[0]] = line[1]
        self.Scores = {}

    @abstractmethod
    def retrieveRequiredFiles(self, query):
        print("Searching...")

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.files = None


class IndexSearcher(Searcher):

    def __init__(self, inputFolder, tokenizer, positionCalc, feedback, rocchioWeights=[], maximumRAM=None):
        """
        Class constructor
        """
        super().__init__(inputFolder, tokenizer, positionCalc, feedback, rocchioWeights, maximumRAM)

    def retrieveRequiredFiles(self, query):
        # {(term,idf):{docid:(weight,[pos1,pos2])}}
        # term:idf;docid:weight:pos1,pos2;docid:weight:pos1,pos2;
        # term:idf;docid:weight;docid:weight;
        # term;docid:tf:pos1,pos2;docid:tf:pos1,pos2;
        # term,docid:tf,docid:tf,

        super().retrieveRequiredFiles(query)

        # tokenize query
        self.tokenizer.tokenize(query.strip())

        # find the index files required
        requiredFiles = []
        for file in self.files:
            aux = file.split("_")
            for t in self.tokenizer.tokens:
                if t > aux[0] and t < aux[1]:
                    requiredFiles.append(self.inputFolder+file)
                    break

        # check if index files are in the correct format
        f = open(requiredFiles[0])
        for line in f:
            # if not, then index is in the wrong format
            assert(":" in line.split(";")[0])
            break

        return requiredFiles

    def calculateScores(self, line, k):
        aux = line.split(";")
        curTerm = aux[0].split(":")[0]
        if curTerm in self.tokenizer.tokens:
            curIdf = float(aux[0].split(":")[1])
            #print("current IDF - " + str(curIdf))
            #print(len(self.tokenizer.tokens) <= 2 or curIdf >= 3.0) 
            if curIdf >= 1.0 or len(self.tokenizer.tokens) <= 2: # only consider high-idf query terms
                for c in aux[1:k+1]: # champions list of size k
                    document = c.split(":")
                    docID = document[0]
                    weight = document[1]
                    if docID not in self.Scores.keys():
                        self.Scores[docID] = round(float(weight), 2)
                        #print("Score - " + str(self.Scores[docID]))
                    else:
                        self.Scores[docID] += round(float(weight), 2)
                        #print("Score - " + str(self.Scores[docID]))
        return

    def sortAndWriteResults(self,outputFile):
        Scores = sorted(self.Scores.items(), key=lambda kv: kv[1], reverse=True)
        outputFile = open(outputFile, "w")
        for (docID, score) in Scores:
            outputFile.write(str(self.translations[docID]) + ", " + str(score) + "\n")
        outputFile.close()
        return

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.files = None
