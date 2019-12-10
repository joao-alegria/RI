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

    """

    def __init__(self, positionCalc, tokenizer, limit, inputFolder, maximumRAM=None, feedback=None, n=None, k=None, rocchioWeights=[]):
        """
        Class constructor
        """
        super().__init__()

        self.files = []
        self.tokenizer = tokenizer
        self.positionCalc = positionCalc
        self.feedback = feedback
        self.rocchioWeights = rocchioWeights

        self.scores = {}
        self.internalCache = {}
        self.k = k
        self.n = n
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
        print("Searching...")

    @abstractmethod
    def calculateScores(self, queryIdx=None):
        return


class IndexSearcher(Searcher):

    def __init__(self, positionCalc, tokenizer, limit, inputFolder, maximumRAM=None, feedback=None, n=None, k=None, rocchioWeights=[]):
        """
        Class constructor
        """
        super().__init__(positionCalc, tokenizer, limit, inputFolder,
                         maximumRAM, feedback, n, k, rocchioWeights)
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
                    if self.internalCache[t][0] > self.max:
                        self.max = self.internalCache[t][0]
                    if self.feedback == "pseudo":
                        assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                        pseudoFeedbackFile = open(
                            "../pseudoFeedback/" + str(self.n) + ".txt", "r")
                        for feedbackLine in pseudoFeedbackFile:
                            content = feedbackLine.split(":")
                            qIdx = int(content[0])
                            if queryIdx == qIdx:
                                alpha = self.rocchioWeights[0]
                                beta = self.rocchioWeights[1]
                                #gamma = self.rocchioWeights[2]
                                relevantDocsSize = int(content[1])
                                relevantSumDj = float(content[2])
                                #irrelevantDocsSize = int(content[3])
                                #irrelevantSumDj = float(content[4])
                                for c in self.internalCache[t][2]:
                                    docID = int(c.split(":")[0])
                                    weight = c.split(":")[1]
                                    # float(weight) * curIdf
                                    s = float(weight) * \
                                        self.internalCache[t][1]
                                    if self.translations[docID-1] not in self.scores.keys():
                                        # + beta*(1/relevantDocsSize)*relevantSumDj - gamma*(1/irrelevantDocsSize)*irrelevantSumDj
                                        self.scores[self.translations[docID-1]
                                                    ] = alpha*s
                                    else:
                                        # + beta*(1/relevantDocsSize)*relevantSumDj - gamma*(1/irrelevantDocsSize)*irrelevantSumDj
                                        self.scores[self.translations[docID-1]
                                                    ] += alpha*s
                                    if relevantDocsSize != 0.0:
                                        self.scores[self.translations[docID-1]
                                                    ] += beta*(1/relevantDocsSize)*relevantSumDj
                    elif self.feedback == "user":
                        assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                        userFeedbackFile = open(
                            "../userFeedback/" + str(self.n) + ".txt", "r")
                        for feedbackLine in userFeedbackFile:
                            content = feedbackLine.split(":")
                            qIdx = int(content[0])
                            if queryIdx == qIdx:
                                alpha = self.rocchioWeights[0]
                                beta = self.rocchioWeights[1]
                                gamma = self.rocchioWeights[2]
                                relevantDocsSize = int(content[1])
                                relevantSumDj = float(content[2])
                                irrelevantDocsSize = int(content[3])
                                irrelevantSumDj = float(content[4])
                                for c in self.internalCache[t][2]:
                                    docID = int(c.split(":")[0])
                                    weight = c.split(":")[1]
                                    s = float(weight) * \
                                        self.internalCache[t][1]
                                    if self.translations[docID-1] not in self.scores.keys():
                                        self.scores[self.translations[docID-1]
                                                    ] = alpha*s
                                    else:
                                        self.scores[self.translations[docID-1]
                                                    ] += alpha*s
                                    if relevantDocsSize != 0.0:
                                        self.scores[self.translations[docID-1]
                                                    ] += beta*(1/relevantDocsSize)*relevantSumDj
                                    if irrelevantDocsSize != 0.0:
                                        self.scores[self.translations[docID-1]] -= gamma * \
                                            (1/irrelevantDocsSize) * \
                                            irrelevantSumDj
                    else:
                        for c in self.internalCache[t][2]:
                            docID = int(c.split(":")[0])
                            weight = c.split(":")[1]
                            if self.translations[docID-1] not in self.scores.keys():
                                self.scores[self.translations[docID-1]
                                            ] = float(weight) * self.internalCache[t][1]
                            else:
                                self.scores[self.translations[docID-1]
                                            ] += float(weight) * self.internalCache[t][1]
            else:  # if file is not in cache
                for line in open(self.inputFolder+f):
                    line = line.strip().split(";")[:self.k+1]
                    curTerm = line[0].split(":")[0]
                    if curTerm in v:
                        v.remove(curTerm)
                        curIdf = float(line[0].split(":")[1])
                        if self.isMemoryAvailable():
                            self.internalCache[curTerm] = [1, curIdf, line[1:]]
                        else:
                            # self.internalCache = {k: v for k, v in self.internalCache.items() if v[0] >= self.max-(self.max/4)}
                            self.internalCache = sorted(
                                self.internalCache.items(), key=lambda tup: tup[1][0], reverse=True)
                            self.internalCache = dict(
                                self.internalCache[:round(len(self.internalCache)/4)])

                        if self.feedback == "pseudo":
                            assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                            pseudoFeedbackFile = open(
                                "../pseudoFeedback/" + str(self.n) + ".txt", "r")
                            for feedbackLine in pseudoFeedbackFile:
                                content = feedbackLine.split(":")
                                qIdx = int(content[0])
                                if queryIdx == qIdx:
                                    alpha = self.rocchioWeights[0]
                                    beta = self.rocchioWeights[1]
                                    #gamma = self.rocchioWeights[2]
                                    relevantDocsSize = int(content[1])
                                    relevantSumDj = float(content[2])
                                    #irrelevantDocsSize = int(content[3])
                                    #irrelevantSumDj = float(content[4])
                                    for c in line[1:]:  # champions list of size k
                                        docID = int(c.split(":")[0])
                                        weight = c.split(":")[1]
                                        s = float(weight) * curIdf
                                        if self.translations[docID-1] not in self.scores.keys():
                                            # + beta*(1/relevantDocsSize)*relevantSumDj - gamma*(1/irrelevantDocsSize)*irrelevantSumDj
                                            self.scores[self.translations[docID-1]
                                                        ] = alpha*s
                                        else:
                                            # + beta*(1/relevantDocsSize)*relevantSumDj - gamma*(1/irrelevantDocsSize)*irrelevantSumDj
                                            self.scores[self.translations[docID-1]
                                                        ] += alpha*s
                                        if relevantDocsSize != 0.0:
                                            self.scores[self.translations[docID-1]] += beta*(
                                                1/relevantDocsSize)*relevantSumDj
                        elif self.feedback == "user":
                            assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                            userFeedbackFile = open(
                                "../userFeedback/" + str(self.n) + ".txt", "r")
                            for feedbackLine in userFeedbackFile:
                                content = feedbackLine.split(":")
                                qIdx = int(content[0])
                                if queryIdx == qIdx:
                                    alpha = self.rocchioWeights[0]
                                    beta = self.rocchioWeights[1]
                                    gamma = self.rocchioWeights[2]
                                    relevantDocsSize = int(content[1])
                                    relevantSumDj = float(content[2])
                                    irrelevantDocsSize = int(content[3])
                                    irrelevantSumDj = float(content[4])
                                    for c in line[1:]:  # champions list of size k
                                        docID = int(c.split(":")[0])
                                        weight = c.split(":")[1]
                                        s = float(weight) * curIdf
                                        if self.translations[docID-1] not in self.scores.keys():
                                            self.scores[self.translations[docID-1]
                                                        ] = alpha*s
                                        else:
                                            self.scores[self.translations[docID-1]
                                                        ] += alpha*s
                                        if relevantDocsSize != 0.0:
                                            self.scores[self.translations[docID-1]] += beta*(
                                                1/relevantDocsSize)*relevantSumDj
                                        if irrelevantDocsSize != 0.0:
                                            self.scores[self.translations[docID-1]] -= gamma*(
                                                1/irrelevantDocsSize)*irrelevantSumDj
                        else:
                            for c in line[1:]:  # champions list of size k
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
        self.curFile = None
        self.curIdx = 0
        self.scores = sorted(self.scores.items(),
                             key=lambda kv: kv[1], reverse=True)
        outputFile = open(outputFile, "w")
        for (PMID, score) in self.scores[:self.limit]:
            outputFile.write(str(PMID) + ", " + str(round(score, 2)) + "\n")
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
