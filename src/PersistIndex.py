"""
.. module:: PersistIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""
import re
import io
import os
import math
from abc import ABC, abstractmethod

LIMITCACHE = 5


class PersistIndex(ABC):
    """
    Abstract class and interface for several types of index persistance implementations, due to file format or processing method

    :param outputFolder: name of the folder were the information should be written too
    :type outputFolder: str
    :param indexer: instance of the indexer used in the context to create the corpus index
    :type indexer: Indexer
    :param totalNumDocs: total number of documents needed if the weights need to be calculated
    :type totalNumDocs: int
    """

    def __init__(self, outputFolder, fileLimit=float("inf"), indexer=None, totalNumDocs=1):
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
            self.index = list(indexer.index.items())
        self.totalNumDocs = totalNumDocs
        self.outputFolder = outputFolder
        self.fileLimit = fileLimit
        self.translationFile = open(outputFolder+"/../indexMetadata.txt", "w")
        self.cacheFile = open("../docCache", "w")

    def setTotalNumDocs(self, totalNumDocs):
        """
        Setter function for the variable totalNumDocs.

        :param: totalNumDocs: number of documents to be processed.
        :type totalNumDocs: int
        """
        self.totalNumDocs = totalNumDocs

    def persistTranslations(self, translations):
        """
        Auxiliary function that persists the index metadata, i.e., the translation from internal ID to PMID(real document identifier).

        :param translations: list of translations.Ex: [(internalID, PMID),...]
        :type translations: list<tuple<str, str>>
        """
        for t in translations:
            self.translationFile.write(t[0]+","+t[1]+"\n")

    def persistCache(self, docID, bestTerms):
        """
        Auxiliary function that persists the a document cache consisting of the documents and the top K best terms.

        :param docID: document identifier
        :type docID: int
        :param bestTerms: list of terms that the indexer considers important
        :type docID: list<str>
        """
        self.cacheFile.write(str(docID)+"".join(";"+str(x[0])+":"+str(x[1])
                                                for x in bestTerms)+"\n")

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
        filenameTemplate = self.currentFilename + "/{}"
        if not overrideFile:
            self.currentFilename = filenameTemplate.format(self.index[0][0])
        f = open(self.currentFilename, "w")
        currStr = ""
        count = 0
        idx = 0
        for token, freqs in self.index:
            currStr += token
            for docID, countPositions in sorted(freqs.items(), key=lambda tup: tup[1], reverse=True):
                currStr += ","+docID+":"+str(countPositions[0])
            # batch-like writting, writting 1 token and its ocurrences at a time
            count += len(currStr)
            f.write(currStr+"\n")
            currStr = ""
            if not overrideFile:
                if count > self.fileLimit:
                    f.close()
                    f = open(filenameTemplate.format(self.index[idx][0]), "w")
                    count = 0
            idx += 1
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
        filenameTemplate = self.currentFilename + "/{}"
        if not overrideFile:
            self.currentFilename = filenameTemplate.format(self.index[0][0])
        f = open(self.currentFilename, "w")
        currStr = ""
        count = 0
        idx = 0
        for token, freqs in self.index:
            currStr += token+":" + \
                str(round(math.log10(self.totalNumDocs/len(freqs)), 2))
            for docID, countPositions in sorted(freqs.items(), key=lambda tup: tup[1], reverse=True):
                currStr += ";"+docID+":" + str(countPositions[0])
            # batch-like writting, writting 1 token and its ocurrences at a time
            count += len(currStr)
            f.write(currStr+"\n")
            currStr = ""
            if not overrideFile:
                if count > self.fileLimit:
                    f.close()
                    f = open(filenameTemplate.format(self.index[idx][0]), "w")
                    count = 0
            idx += 1
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
        filenameTemplate = self.currentFilename + "/{}"
        if not overrideFile:
            self.currentFilename = filenameTemplate.format(self.index[0][0])
        f = open(self.currentFilename, "w")
        currStr = ""
        count = 0
        idx = 0
        for token, freqs in self.index:
            currStr += token
            for docID, countPositions in sorted(freqs.items(), key=lambda tup: tup[1], reverse=True):
                currStr += ";"+docID+":" + \
                    str(countPositions[0])+":"+str(countPositions[1][0]) + \
                    "".join(","+str(x) for x in countPositions[1][1:])
            # batch-like writting, writting 1 token and its ocurrences at a time
            count += len(currStr)
            f.write(currStr+"\n")
            currStr = ""
            if not overrideFile:
                if count > self.fileLimit:
                    f.close()
                    f = open(filenameTemplate.format(self.index[idx][0]), "w")
                    count = 0
            idx += 1
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
        filenameTemplate = self.currentFilename + "/{}"
        if not overrideFile:
            self.currentFilename = filenameTemplate.format(self.index[0][0])
        f = open(self.currentFilename, "w")
        currStr = ""
        count = 0
        idx = 0
        for token, freqs in self.index:
            currStr += token+":" + \
                str(round(math.log10(self.totalNumDocs/len(freqs)), 2))
            for docID, countPositions in sorted(freqs.items(), key=lambda tup: tup[1], reverse=True):
                currStr += ";"+docID+":" + \
                    str(countPositions[0])+":"+str(countPositions[1][0]) + \
                    "".join(","+str(x) for x in countPositions[1][1:])
            # batch-like writting, writting 1 token and its ocurrences at a time

            count += len(currStr)
            f.write(currStr+"\n")
            currStr = ""
            if not overrideFile:
                if count > self.fileLimit:
                    f.close()
                    f = open(filenameTemplate.format(self.index[idx][0]), "w")
                    count = 0
            idx += 1
        f.close()
        del self.index
        self.index = []

        return True

    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        self.index = []
