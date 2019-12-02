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

    def __init__(self, inputFolder, tokenizer, maximumRAM=None):
        """
        Class constructor
        """
        super().__init__()

        self.files = []
        inputFiles = os.listdir(inputFolder)
        for f in inputFiles:
            self.files.append(inputFolder+"/"+f)
        
        self.tokenizer = tokenizer
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

    def __init__(self, inputFolder, tokenizer, maximumRAM):
        """
        Class constructor
        """
        super().__init__(inputFolder, tokenizer, maximumRAM)
        #if self.files != []:
            # ......
        pass

    def processQuery(self,query,outputFile):
        """
        Function that processes the query passed as a string argument.
        """
        super().processQuery(query,outputFile)

        self.tokenizer.tokenize(query)

        weights = {}
        for t in self.tokenizer.tokens: # here weights is actually tfs
            if t not in weights.keys():
                weights[t] = 1
            else:
                weights[t] += 1
        
        norm = 0
        for t in weights.keys(): # now tfs are transformed and normalized
            weights[t] = 1 + math.log10(weights[t]) # * idf                     # ???
            norm += weights[t]**2

        for t in weights.keys(): # finally we have the term weights of the query
            weights[t] = weights[t]/math.sqrt(norm)

        scores = []
        length = []

        requiredFiles = []
        for f in self.files:
            aux = f.split("_")
            for t in weights.keys():
                if t>aux[0] and t<aux[1]:
                    requiredFiles.append(f)
                    break
        
        
        # to do .........
            # fetch postings list for t

            #for d,tf in postings list:
            #    scores[d] += Wt,d * Wt,q

        pass

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.content = None
        self.files = None
        self.docID = None
        self.limit = None
