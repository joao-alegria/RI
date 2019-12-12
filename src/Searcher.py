"""
.. module:: Searcher
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""

import os
import math
import psutil
from abc import ABC, abstractmethod


class Searcher(ABC):
    """
    Abstract class that serves as template and interface for future instances and implementations.

    :param tokenizer: instance of the tokenizer meant to be used
    :type tokenizer: Tokenizer
    :param limit: number of documents that the program should return as result
    :type limit: int
    :param maximumRAM: maximum limit of RAM the program should use
    :type maximumRAM: float
    :param feedback: type of feedback intended to be used, either "pseudo" or "user"
    :type feedback: str
    :param rocchioScope: number of documents that the rocchio algorithm will consider
    :type rocchioScope: int
    :param numChamps: champion list size
    :type numChamps: int
    :param rochhioWeights: contains the paramenters for the rocchio algorithm, need to contain [alpha, beta] for the pseudo feedback and [alpha, beta, gamma] for the user feedback
    :type rocchioWeights: list<float>

    """

    def __init__(self, tokenizer, limit, inputFolder, maximumRAM=None, feedback=None, rocchioScope=None, numChamps=None, rocchioWeights=[]):
        """
        Class constructor
        """
        super().__init__()

        self.files = []
        self.tokenizer = tokenizer
        self.feedback = feedback
        self.rocchioWeights = rocchioWeights

        self.scores = {}
        self.internalCache = {}
        self.numChamps = numChamps
        self.rocchioScope = rocchioScope
        self.limit = limit

        self.maximumRAM = maximumRAM if maximumRAM != None else psutil.virtual_memory().free

        self.inputFolder = inputFolder+"/"
        inputFiles = os.listdir(inputFolder)
        for f in inputFiles:
            self.files.append(f)

        translationFile = open("../indexMetadata.txt")
        self.translations = []
        for line in translationFile:
            line = line.strip().split(",")
            self.translations.append(int(line[1]))

    @abstractmethod
    def retrieveRequiredFiles(self, query):
        """
        Mandatory function that future descendent instances need to implement. Function responsable for obtaining the necessary files to process the query. 

        :param query: query string needed to be processed
        :type query: str
        """
        print("Searching...")

    @abstractmethod
    def calculateScores(self, queryIdx=None):
        """
        Mandatory function that future descendent instances need to implement. Function responsable for calculating the scores for each document. 

        :param queryIdx: optional query identifier
        :type queryIdx: int
        """
        return


class IndexSearcher(Searcher):

    def __init__(self, tokenizer, limit, inputFolder, maximumRAM=None, feedback=None, rocchioScope=None, numChamps=None, rocchioWeights=[]):
        """
        Class constructor
        """
        super().__init__(tokenizer, limit, inputFolder,
                         maximumRAM, feedback, rocchioScope, numChamps, rocchioWeights)
        self.requiredFiles = None

    def retrieveRequiredFiles(self, query):
        """
        In this implementation we take in consideration if the terms are cached in memory.
        """

        # {(term,idf):{docid:(weight,[pos1,pos2])}}
        # term:idf;docid:weight:pos1,pos2;docid:weight:pos1,pos2;
        # term:idf;docid:weight;docid:weight;
        # term;docid:tf:pos1,pos2;docid:tf:pos1,pos2;
        # term,docid:tf,docid:tf,

        super().retrieveRequiredFiles(query)

        # tokenize query
        self.tokenizer.tokenize(query.strip())
        # find the index files required
        self.requiredFiles = {"_cached_": []}
        for t in self.tokenizer.tokens:
            if t in self.internalCache:
                self.requiredFiles["_cached_"].append(t)
            else:
                for file in self.files:
                    aux = file.split("_")
                    if t > aux[0] and t < aux[1]:
                        if file not in self.requiredFiles:
                            self.requiredFiles[file] = [t]
                        else:
                            self.requiredFiles[file].append(t)
                        break

    def calculateScores(self, queryIdx=None):
        for f, v in self.requiredFiles.items():  # for each required file
            if f == "_cached_":  # if file is in cache
                for t in v:
                    self.internalCache[t][0] += 1
                    for docID, weight in self.internalCache[t][2]:
                        if self.translations[int(docID)-1] not in self.scores.keys():
                            self.scores[self.translations[int(docID)-1]
                                        ] = float(weight) * self.internalCache[t][1]
                        else:
                            self.scores[self.translations[int(docID)-1]
                                        ] += float(weight) * self.internalCache[t][1]
            else:  # if file is not in cache
                for line in open(self.inputFolder+f):
                    line = line.strip().split(";")[:self.numChamps+1]
                    curTerm = line[0].split(":")[0]
                    if curTerm in v:
                        v.remove(curTerm)
                        curIdf = float(line[0].split(":")[1])
                        if self.isMemoryAvailable():
                            self.internalCache[curTerm] = [
                                1, curIdf, [(x.split(":")[0], x.split(":")[1]) for x in line[1:]]]
                        else:
                            self.internalCache = sorted(
                                self.internalCache.items(), key=lambda tup: tup[1][0], reverse=True)
                            self.internalCache = dict(
                                self.internalCache[:round(len(self.internalCache)/10)])
                        for c in line[1:]:  # champions list of size numChamps
                            docID = int(c.split(":")[0])
                            weight = c.split(":")[1]
                            if self.translations[docID-1] not in self.scores.keys():
                                self.scores[self.translations[docID-1]
                                            ] = float(weight) * curIdf
                            else:
                                self.scores[self.translations[docID-1]
                                            ] += float(weight) * curIdf
                        if len(v) <= 0:
                            break

    def sortAndWriteResults(self, outputFile):
        """
        Additional function responsable for persisting the query results.

        :param outputFile: name of the file where the results should be stored
        :type outputFile: str
        """

        self.curFile = None
        self.curIdx = 0
        self.scores = sorted(self.scores.items(),
                             key=lambda kv: kv[1], reverse=True)
        outputFile = open(outputFile, "w")
        for (PMID, score) in self.scores[:self.limit]:
            outputFile.write(str(PMID) + ", " +
                             str(round(score, 2)) + "\n")
        outputFile.close()
        self.scores = {}
        return

    def isMemoryAvailable(self):
        """
        Auxiliary function used to determine whether there is still memory available to keep reading information from the input files or not.

        :param maximumRAM: maximum amount of RAM (in Gb) allowed for the program execution
        :type maximumRAM: int
        :returns: True if the memory usage is under 90% of the maximum RAM allowed, false if not
        :rtype: bool

        """
        # pass this verification because if it's to much it's user error
        # if psutil.virtual_memory().percent > 98:  # we avoid using 100% of memory as a prevention measure
        #     return False

        # get program memory usage
        processMemory = psutil.Process(os.getpid()).memory_info().rss
        # print(processMemory)
        if processMemory >= int(self.maximumRAM*0.85):
            return False

        return True
