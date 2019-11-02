import io
import math
from abc import ABC, abstractmethod
from decimal import *

getcontext().prec = 2


class Merger(ABC):
    def __init__(self, filename, intermidiateIndex):
        self.out = open(filename, "w")
        self.files = [io.open(x, "r") for x in intermidiateIndex]
        self.terms = [x.readline().strip().split(";") for x in self.files]
        self.index = {}

    @abstractmethod
    def mergeIndex(self):
        return True

    @classmethod
    def prepareIndex(self):
        pass

    @abstractmethod
    def writeIndex(self):
        pass

    def clearVar(self):
        pass


class PositionWeightMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)
        self.positionIndex = {}

    def mergeIndex(self):
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(";")
            if line == [""]:
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min(self.terms)[0]
        docs = []
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                docs += t[1:]
                self.terms[idx] = ""
        for d in docs:
            docSplitted = d.split(":")
            if term in self.index:
                self.index[term][docSplitted[0]] = docSplitted[1]
                self.positionIndex[term][docSplitted[0]] = docSplitted[2]
            else:
                self.index[term] = {docSplitted[0]: docSplitted[1]}
                self.positionIndex[term] = {
                    docSplitted[0]: docSplitted[2]}
        docs = []
        return False

    def prepareIndex(self):
        for token, postingList in self.index.items():
            for docID, tf in postingList.items():
                postingList[docID] = 1+math.log10(int(tf))
        for token, postingList in self.index.items():
            vectorNorme = math.sqrt(
                sum([math.pow(x, 2) for x in postingList.values()]))
            for docID, tf in postingList.items():
                postingList[docID] = Decimal(
                    postingList[docID])/Decimal(vectorNorme)

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.index = sorted(self.index.items())
        auxString = ""
        idx = 0
        for t, docs in self.index:
            auxString += t
            for doc, w in docs.items():
                auxString += ";"+doc+":" + \
                    str(w)+":"+str(self.positionIndex[t][doc])
            self.out.write(auxString+"\n")
            auxString = ""
            self.positionIndex = {
                x: self.positionIndex[x] for x in self.positionIndex if x != t}
            idx += 1
        self.index = {}


class WeightMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)

    def mergeIndex(self):
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(";")
            if line == [""]:
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min(self.terms)[0]
        docs = []
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                docs += t[1:]
                self.terms[idx] = ""
        for d in docs:
            docSplitted = d.split(":")
            if term in self.index:
                self.index[term][docSplitted[0]] = docSplitted[1]
            else:
                self.index[term] = {docSplitted[0]: docSplitted[1]}
        docs = []
        return False

    def prepareIndex(self):
        for token, postingList in self.index.items():
            for docID, tf in postingList.items():
                postingList[docID] = 1+math.log10(int(tf))
        for token, postingList in self.index.items():
            vectorNorme = math.sqrt(
                sum([math.pow(x, 2) for x in postingList.values()]))
            for docID, tf in postingList.items():
                postingList[docID] = Decimal(
                    postingList[docID])/Decimal(vectorNorme)

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.index = sorted(self.index.items())
        auxString = ""
        idx = 0
        for t, docs in self.index:
            auxString += t
            for doc, w in docs.items():
                auxString += ";"+doc+":" + str(w)
            self.out.write(auxString+"\n")
            auxString = ""
            idx += 1
        self.index = {}


class PositionMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)
        self.positionIndex = {}

    def mergeIndex(self):
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(";")
            if line == [""]:
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min(self.terms)[0]
        docs = []
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                docs += t[1:]
                self.terms[idx] = ""
        for d in docs:
            docSplitted = d.split(":")
            if term in self.index:
                self.index[term][docSplitted[0]] = docSplitted[1]
                self.positionIndex[term][docSplitted[0]] = docSplitted[2]
            else:
                self.index[term] = {docSplitted[0]: docSplitted[1]}
                self.positionIndex[term] = {
                    docSplitted[0]: docSplitted[2]}
        docs = []
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.index = sorted(self.index.items())
        auxString = ""
        idx = 0
        for t, docs in self.index:
            auxString += t
            for doc, w in docs.items():
                auxString += ";"+doc+":" + \
                    str(w)+":"+str(self.positionIndex[t][doc])
            self.out.write(auxString+"\n")
            auxString = ""
            self.positionIndex = {
                x: self.positionIndex[x] for x in self.positionIndex if x != t}
            idx += 1
        self.index = {}


class SimpleMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)

    def mergeIndex(self):
        if self.files == []:
            return True
        if "" in self.terms:
            line = self.files[self.terms.index(
                "")].readline().strip().split(",")
            if line == [""]:
                self.files.remove(self.files[self.terms.index("")])
                self.terms.remove(self.terms[self.terms.index("")])
                return False
            self.terms[self.terms.index("")] = line
            return False

        term = min(self.terms)[0]
        docs = []
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                docs += t[1:]
                self.terms[idx] = ""
        for d in docs:
            docSplitted = d.split(":")
            if term in self.index:
                self.index[term][docSplitted[0]] = docSplitted[1]
            else:
                self.index[term] = {docSplitted[0]: docSplitted[1]}
        docs = []
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.index = sorted(self.index.items())
        auxString = ""
        idx = 0
        for t, docs in self.index:
            auxString += t
            for doc, w in docs.items():
                auxString += ","+doc+":" + str(w)
            self.out.write(auxString+"\n")
            auxString = ""
            idx += 1
        self.index = {}
