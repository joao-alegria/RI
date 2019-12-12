"""
.. module:: Merger
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""
import io
import os
import math
from abc import ABC, abstractmethod
from decimal import *

getcontext().prec = 2


class Merger(ABC):
    """
    Abstract class and interface for several types of index merging implementations, due to file format or processing method

    :param intermediateIndex: list of the names of the intermedia indexes to be merged
    :type intermediateIndex: list<str>
    :param totalNumDocs: total number of documents needed if the weights need to be calculated
    :type totalNumDocs: int
    :param outputFolder: name of the folder where to store the final index
    :type outputFolder: str
    """

    def __init__(self, intermediateIndex, totalNumDocs, outputFolder, fileLimit):
        """
        Class constructor
        """
        # self.out = open(filename, "w")
        self.outFolder = outputFolder
        if not os.path.exists(self.outFolder):
            os.makedirs(self.outFolder)
        else:
            for f in [f for f in os.listdir(self.outFolder)]:
                os.remove(self.outFolder+"/"+f)
        self.files = [io.open(x, "r") for x in intermediateIndex]
        self.index = []
        self.fileLimit = fileLimit
        self.totalNumDocs = totalNumDocs

    @abstractmethod
    def mergeIndex(self):
        """
        Function that merges the intermediate indexes (or blocks of them) into one final index according to our memory-intelligent strategy.
        """
        return True

    @abstractmethod
    def writeIndex(self):
        """
        Function that writes the final index (or blocks of it) to disk according to our memory-intelligent strategy.
        """
        pass

    '''
    def clearVar(self):
        """
        Function that frees the memory currently in use by emptying all class variables.
        """
        pass
    '''


class PositionWeightMerger(Merger):
    def __init__(self, intermediateIndex, totalNumDocs, outputFolder, fileLimit):
        """
        Class constructor
        """
        super().__init__(intermediateIndex, totalNumDocs, outputFolder, fileLimit)
        self.terms = [x.readline().strip().split(";") for x in self.files]

    def mergeIndex(self):
        """
        Variation of the merge function adapted to the positions and weights format.
        """
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(";")
            if line == [""]:
                os.remove(self.files[self.terms.index("")].name)
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min([x[0][:x[0].find(":")] for x in self.terms])
        self.index.append([term, {}])
        for idx, t in enumerate(self.terms):
            if term == t[0][:t[0].find(":")]:
                for d in t[1:]:
                    self.index[-1][1][d.split(":")[0]] = [d.split(":")
                                                          [1], d.split(":")[2].split(",")]
                self.terms[idx] = ""

        return False

    def writeIndex(self):
        """
        Variation of the write function adapted to the positions and weights format.
        """
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        filenameTemplate = self.outFolder + "/{}"
        out = open(filenameTemplate.format(self.index[0][0]), "w")
        auxString = ""
        count = 0
        idx = 0
        for t, docs in self.index:
            auxString += t+":" + \
                str(round(math.log10(self.totalNumDocs/len(docs)), 2))
            for doc, w in sorted(docs.items(), key=lambda tup: tup[1], reverse=True):
                auxString += ";"+doc+":" + w[0] + ":" + \
                    str(w[1][0])+"".join(","+x for x in w[1][1:])
            count += len(auxString)
            out.write(auxString+"\n")
            auxString = ""
            if count > self.fileLimit:
                out.close()
                out = open(filenameTemplate.format(self.index[idx][0]), "w")
                count = 0
            idx += 1
        self.index = []
        out.close()


class WeightMerger(Merger):
    def __init__(self, intermediateIndex, totalNumDocs, outputFolder, fileLimit):
        """
        Class constructor
        """
        super().__init__(intermediateIndex, totalNumDocs, outputFolder, fileLimit)
        self.terms = [x.readline().strip().split(";") for x in self.files]

    def mergeIndex(self):
        """
        Variation of the merge function adapted to the weights format.
        """
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(";")
            if line == [""]:
                os.remove(self.files[self.terms.index("")].name)
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min([x[0][:x[0].find(":")] for x in self.terms])
        self.index.append([term, {}])
        for idx, t in enumerate(self.terms):
            if term == t[0][:t[0].find(":")]:
                for d in t[1:]:
                    self.index[-1][1][d.split(":")[0]] = d.split(":")[1]
                self.terms[idx] = ""

        return False

    def writeIndex(self):
        """
        Variation of the write function adapted to the weights format.
        """
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        filenameTemplate = self.outFolder + "/{}"
        out = open(filenameTemplate.format(self.index[0][0]), "w")
        auxString = ""
        count = 0
        idx = 0
        for t, docs in self.index:
            auxString += t+":" + \
                str(round(math.log10(self.totalNumDocs/len(docs)), 2))
            for doc, w in sorted(docs.items(), key=lambda tup: tup[1], reverse=True):
                auxString += ";"+doc+":" + w
            count += len(auxString)
            out.write(auxString+"\n")
            auxString = ""
            if count > self.fileLimit:
                out.close()
                out = open(filenameTemplate.format(self.index[idx][0]), "w")
                count = 0
            idx += 1
        self.index = []
        out.close()


class PositionMerger(Merger):
    def __init__(self, intermediateIndex, totalNumDocs, outputFolder, fileLimit):
        """
        Class constructor
        """
        super().__init__(intermediateIndex, totalNumDocs, outputFolder, fileLimit)
        self.positionIndex = {}
        self.terms = [x.readline().strip().split(";") for x in self.files]

    def mergeIndex(self):
        """
        Variation of the merge function adapted to the positions format.
        """
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(";")
            if line == [""]:
                os.remove(self.files[self.terms.index("")].name)
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min([x[0] for x in self.terms])
        self.index.append([term, {}])
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                for d in t[1:]:
                    self.index[-1][1][d.split(":")
                                      [0]] = [d.split(":")[1], d.split(":")[2].split(",")]
                self.terms[idx] = ""

        return False

    def writeIndex(self):
        """
        Variation of the write function adapted to the positions format.
        """
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        filenameTemplate = self.outFolder + "/{}"
        out = open(filenameTemplate.format(self.index[0][0]), "w")
        auxString = ""
        count = 0
        idx = 0
        for t, docs in self.index:
            auxString += t
            for doc, w in sorted(docs.items(), key=lambda tup: tup[1], reverse=True):
                auxString += ";"+doc+":" + \
                    str(w[0])+":" + str(w[1][0])+"".join(","+str(x)
                                                         for x in w[1][1:])
            count += len(auxString)
            out.write(auxString+"\n")
            auxString = ""
            if count > self.fileLimit:
                out.close()
                out = open(filenameTemplate.format(self.index[idx][0]), "w")
                count = 0
            idx += 1
        self.index = []
        out.close()


class SimpleMerger(Merger):
    def __init__(self, intermediateIndex, totalNumDocs, outputFolder, fileLimit):
        """
        Class constructor
        """
        super().__init__(intermediateIndex, totalNumDocs, outputFolder, fileLimit)
        self.terms = [x.readline().strip().split(",") for x in self.files]

    def mergeIndex(self):
        """
        Variation of the merge function adapted to the assignment's 1 format.
        """
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(",")
            if line == [""]:
                os.remove(self.files[self.terms.index("")].name)
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min([x[0] for x in self.terms])
        self.index.append([term, {}])
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                for d in t[1:]:
                    self.index[-1][1][d.split(":")[0]] = d.split(":")[1]
                self.terms[idx] = ""

        return False

    def writeIndex(self):
        """
        Variation of the write function adapted to the assignment's 1 format.
        """
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        filenameTemplate = self.outFolder + "/{}"
        out = open(filenameTemplate.format(self.index[0][0]), "w")
        auxString = ""
        count = 0
        idx = 0
        for t, docs in self.index:
            auxString += t
            for doc, w in sorted(docs.items(), key=lambda tup: tup[1], reverse=True):
                auxString += ","+doc+":" + str(w)
            count += len(auxString)
            out.write(auxString+"\n")
            auxString = ""
            if count > self.fileLimit:
                out.close()
                out = open(filenameTemplate.format(self.index[idx][0]), "w")
                count = 0
            idx += 1
        self.index = []
        out.close()
