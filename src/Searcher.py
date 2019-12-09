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

    :param inputFolder: name of the folder containing the files to be used as input
    :type inputFolder: str
    :param tokenizer: instance of the tokenizer used in the context to process the content of the corpus
    :type tokenizer: Tokenizer
    :param maximumRAM: maximum amount of RAM (in Gb) allowed for the program execution
    :type maximumRAM: int

    """

    def __init__(self, inputFolder, tokenizer, positionCalc, K, limit, feedback=None, rocchioWeights=[], maximumRAM=None):
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
        self.maximumRAM = maximumRAM if maximumRAM != None else psutil.virtual_memory().free
        translationFile = open("../indexMetadata.txt")
        self.translations = []
        for line in translationFile:
            line = line.strip().split(",")
            self.translations.append(int(line[1]))
        self.scores = {}
        self.K = K
        self.limit = limit
        self.internalcache = {}

    @abstractmethod
    def retrieveRequiredFiles(self, query):
        print("Searching...")

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.files = None


class IndexSearcher(Searcher):

    def __init__(self, inputFolder, tokenizer, positionCalc, K, limit, feedback, rocchioWeights=[], maximumRAM=None):
        """
        Class constructor
        """
        super().__init__(inputFolder, tokenizer, positionCalc, K, limit,
                         feedback, rocchioWeights, maximumRAM)
        self.requiredFiles = None
        self.max = 0

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
        self.requiredFiles = {"_cached_": []}
        for t in self.tokenizer.tokens:
            if t in self.internalcache:
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

    def calculateScores(self):
        for f, v in self.requiredFiles.items():
            if f == "_cached_":
                for t in v:
                    self.internalcache[t][0] += 1
                    if self.internalcache[t][0] > self.max:
                        self.max = self.internalcache[t][0]
                    for c in self.internalcache[t][2]:
                        docID = c.split(":")[0]
                        weight = c.split(":")[1]
                        if docID not in self.scores:
                            self.scores[docID] = round(
                                float(weight)*self.internalcache[t][1], 2)
                        else:
                            self.scores[docID] += round(float(weight)
                                                        * self.internalcache[t][1], 2)
            else:
                for line in open(self.inputFolder+f):
                    line = line.strip().split(";")[:self.K+1]
                    curTerm = line[0].split(":")[0]
                    if curTerm in v:
                        v.remove(curTerm)
                        curIdf = float(line[0].split(":")[1])
                        if self.isMemoryAvailable():
                            self.internalcache[curTerm] = [1, curIdf, line[1:]]
                        else:
                            # self.internalcache = {k: v for k, v in self.internalcache.items() if v[0] >= self.max-(self.max/4)}
                            self.internalcache = sorted(
                                self.internalcache.items(), key=lambda tup: tup[1][0], reverse=True)
                            self.internalcache = dict(
                                self.internalcache[:round(len(self.internalcache)/4)])
                        for c in line[1:]:  # champions list of size k
                            docID = c.split(":")[0]
                            weight = c.split(":")[1]
                            if docID not in self.scores:
                                self.scores[docID] = round(
                                    float(weight)*curIdf, 2)
                                # print("Score - " + str(self.scores[docID]))
                            else:
                                self.scores[docID] += round(float(weight)
                                                            * curIdf, 2)
                                # print("Score - " + str(self.scores[docID]))
                        if len(v) <= 0:
                            break

    def sortAndWriteResults(self, outputFile):
        self.curFile = None
        self.curIdx = 0
        self.scores = sorted(self.scores.items(),
                             key=lambda kv: kv[1], reverse=True)
        outputFile = open(outputFile, "w")
        for (docID, score) in self.scores[:self.limit]:
            if int(docID)-1 < len(self.translations):
                outputFile.write(
                    str(self.translations[int(docID)-1]) + ", " + str(score) + "\n")
        outputFile.close()
        self.scores = {}
        return

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.files = None

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
