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
        self.maximumRAM = maximumRAM
        self.Scores = {}
        self.k = k
        self.n = n
        self.limit = limit

        self.inputFolder = inputFolder+"/"
        inputFiles = os.listdir(inputFolder)
        for f in inputFiles:
            self.files.append(f)
        
        translationFile = open("../indexMetadata.txt")
        self.translations = {}
        for line in translationFile:
            line = line.strip().split(",")
            self.translations[line[0]] = line[1]
        

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
        self.curFile = None
        self.curIdx = 0
        self.curFilename = ""

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
        self.requiredFiles = {}
        for file in self.files:
            aux = file.split("_")
            for t in self.tokenizer.tokens:
                if t > aux[0] and t < aux[1]:
                    if file not in self.requiredFiles:
                        self.requiredFiles[file] = [t]
                    else:
                        self.requiredFiles[file].append(t)
                    break

        self.requiredFiles = sorted(self.requiredFiles.items())

    def calculateScores(self,queryIdx=None):
        if self.curFile == None:
            if self.curIdx >= len(self.requiredFiles):
                return True
            self.curFile = open(self.inputFolder+self.requiredFiles[self.curIdx][0])
            self.curFilename = self.requiredFiles[self.curIdx][0]
        for line in self.curFile:
            line = line.split(";")
            curTerm = line[0].split(":")[0]
            if curTerm in self.requiredFiles[self.curIdx][1]:
                self.requiredFiles[self.curIdx][1].remove(curTerm)
                curIdf = float(line[0].split(":")[1])
                # only consider high-idf query terms
                # if curIdf >= 1.0 or len(self.tokenizer.tokens) <= 2:
                if self.feedback=="pseudo":
                    assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                    pseudoFeedbackFile = open("../pseudoFeedback/" + str(self.n) + ".txt","r")
                    for feedbackLine in pseudoFeedbackFile:
                        content = feedbackLine.split(":")
                        qIdx = int(content[0])
                        if queryIdx==qIdx:
                            relevantPMIDs = content[1].split(",")
                            irrelevantPMIDs = content[2].split(",")
                            alpha = self.rocchioWeights[0]
                            beta = self.rocchioWeights[1]
                            gamma = self.rocchioWeights[2]
                            for c in line[1:self.k]:  # champions list of size k
                                docID = c.split(":")[0]
                                weight = c.split(":")[1]
                                s = round(float(weight) * curIdf, 2)
                                if docID not in self.Scores:
                                    self.Scores[self.translations[docID]] = alpha*s + beta*(1/len(relevantPMIDs))*s - gamma*(1/len(irrelevantPMIDs))*s
                                else:
                                    self.Scores[self.translations[docID]] += alpha*s + beta*(1/len(relevantPMIDs))*s - gamma*(1/len(irrelevantPMIDs))*s
                elif self.feedback=="user":
                    assert self.n, "Error: integer n defines the number of docs to be considered relevant in pseudo feedback, if you want this feedback you must define this value"
                    userFeedbackFile = open("../userFeedback/" + str(self.n) + ".txt","r")
                    
                else:
                    for c in line[1:self.k]:  # champions list of size k
                        docID = c.split(":")[0]
                        weight = c.split(":")[1]
                        if docID not in self.Scores:
                            self.Scores[self.translations[docID]] = round(float(weight) * curIdf, 2)
                            #print("Score - " + str(self.Scores[docID]))
                        else:
                            self.Scores[self.translations[docID]] += round(float(weight) * curIdf, 2)
                            #print("Score - " + str(self.Scores[docID]))
                if len(self.requiredFiles[self.curIdx][1]) <= 0:
                    self.curFile = None
                    self.curIdx += 1
                    return False
            return False
        self.curFile = None
        self.curIdx += 1
        return False

    def sortAndWriteResults(self, outputFile):
        self.curFile = None
        self.curIdx = 0
        self.curFilename = ""
        Scores = sorted(self.Scores.items(), key=lambda kv: kv[1], reverse=True)
        outputFile = open(outputFile, "w")
        for (PMID, score) in Scores[:self.limit]:
            outputFile.write(str(PMID) + ", " + str(score) + "\n")
        outputFile.close()
        return

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.files = None


# Scores = {}
#         for file in requiredFiles:
#             f = open(file, "r")
#             for line in f:
#                 aux = line.split(";")
#                 curTerm = aux[0].split(":")[0]
#                 if curTerm in self.tokenizer.tokens:
#                     curIdf = float(aux[0].split(":")[1])
#                     for c in aux[1:K+1]:
#                         document = c.split(":")
#                         docID = document[0]
#                         weight = document[1]
#                         if docID not in Scores:
#                             Scores[docID] = float(weight)*curIdf
#                         else:
#                             Scores[docID] += float(weight)*curIdf
