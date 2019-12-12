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
        self.files = sorted(self.files)

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
        self.max = 0

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
                for i,file in enumerate(self.files):
                    if t > file:
                        if i==len(self.files)-1 or t<self.files[i+1]:
                            if file not in self.requiredFiles:
                                self.requiredFiles[file] = [t]
                            else:
                                self.requiredFiles[file].append(t)
                            break

    def calculateScores(self, queryIdx=None):
        queryTermsIdf = {}

        for f, v in self.requiredFiles.items():  # for each required file
            if f == "_cached_":  # if file is in cache
                for t in v:
                    self.internalCache[t][0] += 1
                    if self.internalCache[t][0] > self.max:
                        self.max = self.internalCache[t][0]

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
                    line = line.strip().split(";")[:self.numChamps+1]
                    curTerm = line[0].split(":")[0]
                    if curTerm in v:
                        v.remove(curTerm)
                        curIdf = float(line[0].split(":")[1])
                        if self.isMemoryAvailable():
                            self.internalCache[curTerm] = [1, curIdf, line[1:]]
                        else:
                            # self.internalCache = {numChamps: v for numChamps, v in self.internalCache.items() if v[0] >= self.max-(self.max/4)}
                            self.internalCache = sorted(
                                self.internalCache.items(), key=lambda tup: tup[1][0], reverse=True)
                            self.internalCache = dict(
                                self.internalCache[:round(len(self.internalCache)/4)])

                        for c in line[1:]:  # champions list of size numChamps
                            docID = int(c.split(":")[0])
                            weight = c.split(":")[1]
                            if self.translations[docID-1] not in self.scores.keys():
                                self.scores[self.translations[docID-1]
                                            ] = float(weight) * curIdf
                            else:
                                self.scores[self.translations[docID-1]
                                            ] += float(weight) * curIdf
                            queryTermsIdf[curTerm] = curIdf

                        if len(v) <= 0:
                            break
        
        if self.feedback:
            assert self.rocchioScope, "Error: integer rocchioScope defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
            
            indexCacheFile = open("indexCache") # index cache -> docID;term:weight;term:weight;...

            alpha = self.rocchioWeights[0]
            beta = self.rocchioWeights[1]

            relevantDocs = []
            #relevantSumDj = 0.0

            for t in queryTermsIdf.keys():
                queryTermsIdf[t] = queryTermsIdf[t]*alpha

            if self.feedback == "pseudo":
                for s in self.scores[:self.rocchioScope]:
                    relevantDocs.append(s[0])
                
                for line in indexCacheFile:
                    content = line.split(";")
                    if int(content[0]) in relevantDocs:
                        newTokens = []
                        for d in content[1:]:
                            d = d.split(":")
                            newTokens.append(d[0])
                            if d[0] in queryTermsIdf.keys():
                                queryTermsIdf[d[0]] += beta*float(d[1])/len(relevantDocs)
                            else:
                                queryTermsIdf[d[0]] = beta*float(d[1])/len(relevantDocs)
                        self.tokenizer.tokens = self.tokenizer.tokens + newTokens

            else: # == "user"
                gamma = self.rocchioWeights[2]
                irrelevantDocs = []
                #irrelevantSumDj = 0.0
                
                gold = {}
                for standard in open("../queries.relevance.txt"):
                    line = standard.strip().split("\t")
                    if int(line[0]) not in gold:
                        gold[int(line[0])] = [int(line[1])]
                    else:
                        gold[int(line[0])].append(int(line[1]))

                i = 0
                for s in self.scores:
                    if i >= self.rocchioScope:
                        break
                    if s[0] in gold[self.translations[int(queryIdx)-1]]:
                        relevantDocs.append(s[0])
                    else:
                        irrelevantDocs.append(s[0])
                    i += 1

                for line in indexCacheFile:
                    content = line.split(";")
                    if int(content[0]) in relevantDocs:
                        newTokens = []
                        for d in content[1:]:
                            d = d.split(":")
                            newTokens.append(d[0])
                            if d[0] in queryTermsIdf.keys():
                                queryTermsIdf[d[0]] += beta*float(d[1])/len(relevantDocs)
                            else:
                                queryTermsIdf[d[0]] = beta*float(d[1])/len(relevantDocs)
                        self.tokenizer.tokens = self.tokenizer.tokens + newTokens
                indexCacheFile.seek(0, 0)
                for line in indexCacheFile:
                    content = line.split(";")
                    if int(content[0]) in irrelevantDocs:
                        for d in content[1:]:
                            d = d.split(":")
                            if d[0] in queryTermsIdf.keys():
                                queryTermsIdf[d[0]] -= gamma*float(d[1])/len(irrelevantDocs)

            indexCacheFile.close()

            self.requiredFiles = {"_cached_": []}
            for t in self.tokenizer.tokens:
                if t in self.internalCache:
                    self.requiredFiles["_cached_"].append(t)
                else:
                    for i,file in enumerate(self.files):
                        if t > file:
                            if i==len(self.files)-1 or t<self.files[i+1]:
                                if file not in self.requiredFiles:
                                    self.requiredFiles[file] = [t]
                                else:
                                    self.requiredFiles[file].append(t)
                                break

            for f, v in self.requiredFiles.items():  # for each required file
                if f == "_cached_":  # if file is in cache
                    for t in v:
                        self.internalCache[t][0] += 1
                        if self.internalCache[t][0] > self.max:
                            self.max = self.internalCache[t][0]

                        for c in self.internalCache[t][2]:
                            docID = int(c.split(":")[0])
                            weight = c.split(":")[1]
                            if self.translations[docID-1] not in self.scores.keys():
                                self.scores[self.translations[docID-1]
                                            ] = float(weight) * queryTermsIdf[t]
                            else:
                                self.scores[self.translations[docID-1]
                                            ] += float(weight) * queryTermsIdf[t]

                else:  # if file is not in cache
                    for line in open(self.inputFolder+f):
                        line = line.strip().split(";")[:self.numChamps+1]
                        curTerm = line[0].split(":")[0]
                        if curTerm in v:
                            v.remove(curTerm)
                            curIdf = float(line[0].split(":")[1])
                            if self.isMemoryAvailable():
                                self.internalCache[curTerm] = [1, curIdf, line[1:]]
                            else:
                                # self.internalCache = {numChamps: v for numChamps, v in self.internalCache.items() if v[0] >= self.max-(self.max/4)}
                                self.internalCache = sorted(
                                    self.internalCache.items(), key=lambda tup: tup[1][0], reverse=True)
                                self.internalCache = dict(
                                    self.internalCache[:round(len(self.internalCache)/4)])

                            for c in line[1:]:  # champions list of size numChamps
                                docID = int(c.split(":")[0])
                                weight = c.split(":")[1]
                                if self.translations[docID-1] not in self.scores.keys():
                                    self.scores[self.translations[docID-1]
                                                ] = float(weight) * queryTermsIdf[t]
                                else:
                                    self.scores[self.translations[docID-1]
                                                ] += float(weight) * queryTermsIdf[t]

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
