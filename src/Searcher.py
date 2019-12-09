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
        self.internalcache = {}
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

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.files = None


class IndexSearcher(Searcher):

    def __init__(self, positionCalc, tokenizer, limit, inputFolder, maximumRAM=None, feedback=None, n=None, k=None, rocchioWeights=[]):
        """
        Class constructor
        """
        super().__init__(positionCalc, tokenizer, limit, inputFolder, maximumRAM, feedback, n, k, rocchioWeights)
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

    def calculateScores(self,queryIdx=None):
        for f, v in self.requiredFiles.items():
            if f == "_cached_":
                for t in v:
                    self.internalcache[t][0] += 1
                    if self.internalcache[t][0] > self.max:
                        self.max = self.internalcache[t][0]
                    if self.feedback=="pseudo":
                        assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                        pseudoFeedbackFile = open("../pseudoFeedback/" + str(self.n) + ".txt","r")
                        for feedbackLine in pseudoFeedbackFile:
                            content = feedbackLine.split(":")
                            qIdx = int(content[0])
                            if queryIdx==qIdx:
                                relevantPMIDs = content[1].split(",")
                                #irrelevantPMIDs = content[2].split(",")
                                alpha = self.rocchioWeights[0]
                                beta = self.rocchioWeights[1]
                                #gamma = self.rocchioWeights[2]
                                for c in self.internalcache[t][2]:
                                    docID = int(c.split(":")[0])
                                    weight = c.split(":")[1]
                                    s = round(float(weight) * self.internalcache[t][1], 2) # round(float(weight) * curIdf, 2)
                                    if self.translations[docID-1] not in self.scores.keys():
                                        self.scores[self.translations[docID-1]] = alpha*s + beta*(1/len(relevantPMIDs))*s #- gamma*(1/len(irrelevantPMIDs))*s
                                    else:
                                        self.scores[self.translations[docID-1]] += alpha*s + beta*(1/len(relevantPMIDs))*s #- gamma*(1/len(irrelevantPMIDs))*s
                    elif self.feedback=="user":
                        assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                        userFeedbackFile = open("../userFeedback/" + str(self.n) + ".txt","r")

                    else:
                        for c in self.internalcache[t][2]:
                            docID = int(c.split(":")[0])
                            weight = c.split(":")[1]
                            if self.translations[docID-1] not in self.scores.keys():
                                self.scores[self.translations[docID-1]] = round(float(weight) * self.internalcache[t][1], 2)
                            else:
                                self.scores[self.translations[docID-1]] += round(float(weight) * self.internalcache[t][1], 2)
            else:
                for line in open(self.inputFolder+f):
                    line = line.strip().split(";")[:self.k+1]
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

                        if self.feedback=="pseudo":
                            assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                            pseudoFeedbackFile = open("../pseudoFeedback/" + str(self.n) + ".txt","r")
                            for feedbackLine in pseudoFeedbackFile:
                                content = feedbackLine.split(":")
                                qIdx = int(content[0])
                                if queryIdx==qIdx:
                                    relevantPMIDs = content[1].split(",")
                                    #irrelevantPMIDs = content[2].split(",")
                                    alpha = self.rocchioWeights[0]
                                    beta = self.rocchioWeights[1]
                                    #gamma = self.rocchioWeights[2]
                                    for c in line[1:]:  # champions list of size k
                                        docID = int(c.split(":")[0])
                                        weight = c.split(":")[1]
                                        s = round(float(weight) * curIdf, 2)
                                        if self.translations[docID-1] not in self.scores.keys():
                                            self.scores[self.translations[docID-1]] = alpha*s + beta*(1/len(relevantPMIDs))*s #- gamma*(1/len(irrelevantPMIDs))*s
                                        else:
                                            self.scores[self.translations[docID-1]] += alpha*s + beta*(1/len(relevantPMIDs))*s #- gamma*(1/len(irrelevantPMIDs))*s
                        elif self.feedback=="user":
                            assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                            userFeedbackFile = open("../userFeedback/" + str(self.n) + ".txt","r")
                            
                        else:
                            for c in line[1:]:  # champions list of size k
                                docID = int(c.split(":")[0])
                                weight = c.split(":")[1]
                                if self.translations[docID-1] not in self.scores.keys():
                                    self.scores[self.translations[docID-1]] = round(float(weight) * curIdf, 2)
                                else:
                                    self.scores[self.translations[docID-1]] += round(float(weight) * curIdf, 2)
                        if len(v) <= 0:
                            break

    def sortAndWriteResults(self, outputFile):
        self.curFile = None
        self.curIdx = 0
        self.scores = sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)
        outputFile = open(outputFile, "w")
        for (PMID, score) in self.scores[:self.limit]:
            outputFile.write(str(PMID) + ", " + str(score) + "\n")
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
