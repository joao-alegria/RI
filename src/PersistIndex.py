"""
.. module:: PersistIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""
import re
import io
import os
from abc import ABC, abstractmethod


class PersistIndex(ABC):
    """
    Abstract class and interface for several types of index persistance implementations, due to file format or processing method

    :param outputFolder: name of the folder were the information should be written too
    :type outputFolder: str
    :param indexer: instance of the indexer used in the context to create the corpus index
    :type indexer: Indexer
    """

    def __init__(self, outputFolder, indexer=None):
        """
        Class constructor
        """
        super().__init__()
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        else:
            for f in [f for f in os.listdir(outputFolder)]:
                os.remove(outputFolder+"/"+f)
        if indexer:
            indexer.createIndex()
            self.index = list(indexer.index.items())
            self.indexer = indexer
        self.outputFolder = outputFolder

    @abstractmethod
    def persist(self, index=None, overrideFile=None):
        """
        Function that effectively persists the data.
        """
        if index:
            self.index = list(index.items())
        if overrideFile:
            self.currentFilename = overrideFile
        else:
            self.currentFilename = self.outputFolder
        if self.index == []:
            return False
        print("Persisting...")

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = []


class PersistCSV(PersistIndex):
    """
    Implementation of the index persister dedicated to first assignment. This instance persists the index in a text file, following a CSV-like format, such as:
        token1,docID1:numOcur,docID2:numOcur,...
        token2,docID1:numOcur,docID2:numOcur,...
    """

    def persist(self, index=None, overrideFile=None):
        """
        Function that effectively persists the data in a CSV format.
        """
        super().persist(index, overrideFile)
        if self.index == []:
            return False
        self.index.sort(key=lambda tup: tup[0])
        if not overrideFile:
            self.currentFilename = self.currentFilename + \
                "/"+self.index[0][0]+"_"+self.index[-1][0]
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            currStr += token
            for docID, count in freqs.items():
                currStr += ","+docID+":"+str(count)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = []
        return True

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = []


class PersistCSVWeighted(PersistIndex):
    """
    Implementation of the index persister dedicated to the second assignment. This instance persists the index in a text file, following a CSV-like format, such as:
        token1:idf1; docID1:tfw1; docID2:tfw2;...
        token2:idf2; docID1:tfw1; docID2:tfw2;...
    """

    def persist(self, index=None, overrideFile=None):
        super().persist(index, overrideFile)
        if self.index == []:
            return False
        self.index.sort(key=lambda tup: tup[0])
        if not overrideFile:
            self.currentFilename = self.currentFilename + \
                "/"+self.index[0][0]+"_"+self.index[-1][0]
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            idf, w = self.indexer.normalize(freqs)
            currStr += token+":"+str(idf)
            for docID, fr in freqs.items():
                currStr += ";"+docID+":"+str(fr if overrideFile else w[0])
                w = w[1:]
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = []
        return True

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = []


class PersistCSVPosition(PersistIndex):
    """
    Implementation of the index persister dedicated to the second assignment. This instance persists the index in a text file, following a CSV-like format, such as:
        token1,docID1:docFreq1:pos1,pos2,...; docID2:docFreq2:pos1,pos2,...; ...
        token2,docID1:docFreq1:pos1,pos2,...; docID2:docFreq1:pos1,pos2,...; ...
    """

    def persist(self, index=None, overrideFile=None):
        super().persist(index, overrideFile)
        if self.index == []:
            return False
        self.index.sort(key=lambda tup: tup[0])
        if not overrideFile:
            self.currentFilename = self.currentFilename + \
                "/"+self.index[0][0]+"_"+self.index[-1][0]
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            currStr += token
            for docID, pos in freqs.items():
                currStr += ";"+docID+":" + \
                    str(len(pos))+":"+str(pos[0]) + \
                    "".join(","+str(x) for x in pos[1:])
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = []
        return True

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = []


class PersistCSVWeightedPosition(PersistIndex):
    """
    Implementation of the index persister dedicated to the second assignment. This instance persists the index in a text file, following a CSV-like format, such as:
        token1:idf1; docID1:tfw1:pos1,pos2,...; docID2:tfw2:...; ...
        token2:idf2; docID1:tfw1:pos1,pos2,...; docID2:tfw2:...; ...
    """

    def persist(self, index=None, overrideFile=None):
        super().persist(index, overrideFile)
        if self.index == []:
            return False
        self.index.sort(key=lambda tup: tup[0])
        if not overrideFile:
            self.currentFilename = self.currentFilename + \
                "/"+self.index[0][0]+"_"+self.index[-1][0]
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.index:
            idf, w = self.indexer.normalize(freqs)
            currStr += token+":"+str(idf)
            for docID, pos in freqs.items():
                currStr += ";"+docID+":" + \
                    str(len(pos) if overrideFile else w[0])+":"+str(pos[0]) + "".join(","+str(x)
                                                                                      for x in pos[1:])
                w = w[1:]
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        self.index = []

        return True

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = []
