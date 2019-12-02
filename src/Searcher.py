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

    def __init__(self, inputFolder, tokenizer, positionCalc, maximumRAM=None):
        """
        Class constructor
        """
        super().__init__()

        self.files = []
        inputFiles = os.listdir(inputFolder)
        for f in inputFiles:
            self.files.append(inputFolder+"/"+f)
        
        self.tokenizer = tokenizer
        self.positionCalc = positionCalc
        self.maximumRAM = maximumRAM

    @abstractmethod
    def processQuery(self,query,outputFile):
        """
        Function that processes the query passed as a string argument.
        """
        print("Searching...")
        pass

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.content = None
        self.files = None
        self.docID = None


class IndexSearcher(Searcher):

    def __init__(self, inputFolder, tokenizer, positionCalc, maximumRAM=None):
        """
        Class constructor
        """
        super().__init__(inputFolder, tokenizer, positionCalc, maximumRAM)
        #if self.files != []:
            # ......
        pass

    def processQuery(self,query,outputFile):
        """
        Function that processes the query passed as a string argument.
        """
        super().processQuery(query,outputFile)

        # {(term,idf):{docid:(weight,[pos1,pos2])}}    
        # term:idf;docid:weight:pos1,pos2;docid:weight:pos1,pos2;
        # term:idf;docid:weight;docid:weight;
        # term;docid:tf:pos1,pos2;docid:tf:pos1,pos2;
        # term,docid:tf,docid:tf,

        # tokenize query
        self.tokenizer.tokenize(query.strip())

        # start calculating weights of each token in the query
        weights = {}
        for t in self.tokenizer.tokens: # here weights is actually tfs
            if t not in weights.keys():
                weights[t] = 1
            else:
                weights[t] += 1

        # find the index files required
        requiredFiles = []
        for file in self.files:
            aux = file.split("_")
            for t in weights.keys():
                if t>aux[0] and t<aux[1]:
                    requiredFiles.append(file)
                    break

        # check if index files are in the correct format
        f = open(requiredFiles[0])
        for line in f:
            assert(":" in line.split(";")[0]) # if not, then index is in the wrong format
            break
        
        # retrieve the desired postings lists
        postingsLists = {}
        for file in requiredFiles:
            f = open(file,"r")
            for line in f:
                aux = line.split(";")
                curTerm = aux[0].split(":")[0]
                for t in weights.keys():
                    if curTerm == t:
                        curIdf = float(aux[0].split(":")[1])
                        content = {}
                        if self.positionCalc:
                            for c in aux[1:]:
                                document = c.split(":")
                                docID = int(document[0])
                                weight = float(document[1])
                                positions = []
                                if "," in document[2]:
                                    strPos = document[2].split(",")
                                    for s in strPos:
                                        positions.append(int(s))
                                else:
                                    positions.append(document[2])
                                content[docID] = (weight,positions)
                        else:
                            for c in aux[1:]:
                                document = c.split(":")
                                docID = document[0]
                                weight = document[1]
                                content[docID] = weight
                        postingsLists[(t,curIdf)] = content

        # finish calculating weights of each token in the query and normalize them
        norm = 0
        for t in weights.keys(): # now tfs are transformed and normalized
            idf = 0
            for key in postingsLists.keys():
                if key[0] == t:
                    idf = key[1]
            weights[t] = 1 + math.log10(weights[t]) * idf 
            norm += weights[t]**2

        for t in weights.keys(): # finally we have the term weights of the query
            weights[t] = weights[t]/math.sqrt(norm)

        # calculate the score of each document
        Scores = {}
        for key in postingsLists.keys():
            for docID in postingsLists[key].keys():
                if self.positionCalc:
                    if docID not in Scores.keys():
                        Scores[docID] = postingsLists[key][docID][0] * weights[key[0]]
                    else:
                        Scores[docID] += postingsLists[key][docID][0] * weights[key[0]]
                else:
                    if docID not in Scores.keys():
                        Scores[docID] = postingsLists[key][docID] * weights[key[0]]
                    else:
                        Scores[docID] += postingsLists[key][docID] * weights[key[0]]
        
        # sort results and write them 
        Scores = sorted(Scores.items(), key=lambda kv: kv[1],reverse=True)
        outputFile = open(outputFile,"w")
        for (docID,score) in Scores:
            outputFile.write(str(docID) + ", " + str(score) + "\n")
        outputFile.close()
        
        return


    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.content = None
        self.files = None
        self.docID = None
        self.limit = None
