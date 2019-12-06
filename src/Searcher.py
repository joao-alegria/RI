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

    def __init__(self, inputFolder, tokenizer, maximumRAM=None):
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
        translationFile = open("../indexMetadata.txt")
        self.translations = {}
        for line in translationFile:
            line = line.strip().split(",")
            self.translations[line[0]] = line[1]

    @abstractmethod
    def processQuery(self, query, outputFile):
        """
        Function that processes the query passed as a string argument.
        """
        print("Searching...")
        pass

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.files = None


class IndexSearcher(Searcher):

    def __init__(self, inputFolder, tokenizer, maximumRAM=None):
        """
        Class constructor
        """
        super().__init__(inputFolder, tokenizer, maximumRAM)
        # if self.files != []:
        # ......
        pass

    def processQuery(self, query, outputFile):
        """
        Function that processes the query passed as a string argument.
        """
        super().processQuery(query, outputFile)

        # {(term,idf):{docid:(weight,[pos1,pos2])}}
        # term:idf;docid:weight:pos1,pos2;docid:weight:pos1,pos2;
        # term:idf;docid:weight;docid:weight;
        # term;docid:tf:pos1,pos2;docid:tf:pos1,pos2;
        # term,docid:tf,docid:tf,

        # tokenize query
        self.tokenizer.tokenize(query.strip())

        # start calculating weights of each token in the query
        # weights = {}
        # for t in self.tokenizer.tokens:  # here weights is actually tfs
        #     if t not in weights.keys():
        #         weights[t] = 1
        #     else:
        #         weights[t] += 1

        # find the index files required
        requiredFiles = {}
        for file in self.files:
            aux = file.split("_")
            for t in self.tokenizer.tokens:
                if t > aux[0] and t < aux[1]:
                    if file not in requiredFiles:
                        requiredFiles[file] = [t]
                    else:
                        requiredFiles[file].append(t)
                    break

        K = 200

        # retrieve the desired postings lists
        # postingsLists = {}
        Scores = {}
        for file in requiredFiles:
            f = open(self.inputFolder+"/"+file, "r")
            for line in f:
                # assert(":" in line.split(";")[0])
                aux = line.split(";")
                curTerm = aux[0].split(":")[0]
                if curTerm in requiredFiles[file]:
                    requiredFiles[file].remove(curTerm)
                    curIdf = float(aux[0].split(":")[1])
                    # content = {}
                    for c in aux[1:K+1]:
                        document = c.split(":")
                        docID = document[0]
                        weight = document[1]
                        if docID not in Scores:
                            Scores[docID] = float(weight)*curIdf
                        else:
                            Scores[docID] += float(weight)*curIdf
                    # postingsLists[curIdf] = content
                    if len(requiredFiles[file]) <= 0:
                        break

        # finish calculating weights of each token in the query and normalize them
        # norm = 0
        # for t in weights:  # now tfs are transformed and normalized
        #     idf = 0
        #     for key in postingsLists.keys():
        #         if key[0] == t:
        #             idf = key[1]
        #     weights[t] = (1 + math.log10(weights[t])) * idf
        #     norm += weights[t]**2

        # for t in weights:  # finally we have the term weights of the query
        #     weights[t] = weights[t]/math.sqrt(norm) if math.sqrt(norm) else 0.0

        # calculate the score of each document
        # Scores = {}
        # postingsLists = sorted(postingsLists.items(), reverse=True)
        # bestIDF = postingsLists[0][0]
        # for idf, docs in postingsLists:
        #     for docID in docs:
        #         if idf not in Scores:
        #             Scores[docID] = docs[docID]
        #         else:
        #             Scores[docID] += docs[docID]
        #         # if docID not in Scores:
        #         #     Scores[docID] = docs[docID]
        #         # else:
        #         #     Scores[docID] += docs[docID]

        # sort results and write them
        Scores = sorted(Scores.items(), key=lambda kv: kv[1], reverse=True)
        outputFile = open(outputFile, "w")
        for (docID, score) in Scores[:10]:
            outputFile.write(
                str(self.translations[docID]) + ", " + str(round(score, 2)) + "\n")
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
