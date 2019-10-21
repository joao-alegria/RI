"""
.. module:: PersistIndex
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""
import re
import io
from abc import ABC, abstractmethod


class PersistIndex(ABC):
    """
    Abstract class and interface for several types of index persistance implementations, due to file format or processing method

    :param filename: name of the file were the information should be written too
    :type filename: str
    :param indexer: instance of the indexer used in the context to create the corpus index
    :type indexer: Indexer
    """

    def __init__(self, filename, indexer=None):
        """
        Class constructor
        """
        if indexer:
            indexer.createIndex()
            self.content = indexer.normalizeIndex()
        self.filename = filename
        super().__init__()

    @abstractmethod
    def persist(self, content=None, overrideFile=None):
        """
        Function that effectively persists the data.
        """
        if content:
            self.content = content
        if overrideFile:
            self.currentFilename = overrideFile
        else:
            self.currentFilename = self.filename
        if self.content == {}:
            return False
        print("Persisting...")

    @abstractmethod
    def mergeIndex(self, intermideiateIndex):
        print("Merging...")
        pass


class PersistCSV(PersistIndex):
    """
    Implementation of the index persister dedicated to the current context of RI. This instance persists the index in a text file, following a csv-like format, such as:
        token1,docID1:numOcur,docID2:numOcur,...
        token2,docID1:numOcur,docID2:numOcur,...
    """

    def persist(self, content=None, overrideFile=None):
        super().persist(content, overrideFile)
        self.content = sorted(self.content.items())
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.content:
            currStr += token
            for docID, count in freqs.items():
                currStr += ","+docID+":"+str(count)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        return True

    def mergeIndex(self, intermidiateIndex):
        # TODO
        pass


class PersistCSVWeighted(PersistIndex):
    def persist(self, content=None, overrideFile=None):
        super().persist(content, overrideFile)
        self.content = sorted(self.content.items())
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in self.content:
            currStr += token+":1"
            for docID, count in freqs.items():
                currStr += ";"+docID+":"+str(count)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        return True

    def mergeIndex(self, intermidiateIndex):
        # TODO
        pass


class PersistCSVWeightedPosition(PersistIndex):
    def persist(self, content=None, overrideFile=None):
        super().persist(content, overrideFile)
        if self.content == ({}, {}):
            return False
        index, positions = self.content
        index = sorted(index.items())
        f = open(self.currentFilename, "w")
        currStr = ""
        for token, freqs in index:
            currStr += token+":1"
            for docID, count in freqs.items():
                currStr += ";"+docID+":" + \
                    str(count)+":"+str(positions[token][docID][0])
                for pos in positions[token][docID][1:]:
                    currStr += ","+str(pos)
            # batch-like writting, writting 1 token and its ocurrences at a time
            f.write(currStr+"\n")
            currStr = ""
        f.close()
        return True

    def mergeIndex(self, intermidiateIndex):
        # TODO: when reached ram total
        safeIdx = 0
        sortedTerms = []

        files = [io.open(x, "r") for x in intermidiateIndex]
        line = files[0].readline().strip().split(";")
        currentTerm = line[0]

        terms = {line[0]: line[1:]}
        sortedTerms.append(line[0])
        while files != []:
            for f in files:
                line = f.readline().strip().split(";")
                if line == [""]:
                    files.remove(f)
                    continue
                if line[0] in terms:
                    terms[line[0]] += line[1:]
                else:
                    terms[line[0]] = line[1:]
                    sortedTerms.append(line[0])
                    sorted(sortedTerms)
            safeIdx += 1

        out = open(self.filename, "w")
        auxString = ""
        print(sortedTerms)
        for t in sortedTerms:
            auxString += t
            for doc in terms[t]:
                auxString += ";"+doc
            out.write(auxString+"\n")
            auxString = ""
