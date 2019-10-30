import io
import math
from abc import ABC, abstractmethod
from decimal import *

getcontext().prec = 2


class Merger(ABC):
    def __init__(self, filename, intermidiateIndex):
        self.out = open(filename, "w")
        self.files = [io.open(x, "r") for x in intermidiateIndex]
        self.safeTerm = ""
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


class PositionWeightMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)
        self.positionIndex = {}

    def mergeIndex(self):
        # TODO remove files
        currentTerms = []
        for f in self.files:
            line = f.readline().strip().split(";")
            term = line[0]
            currentTerms.append(term)
            if line == [""]:
                self.files.remove(f)
                continue
            for docs in line[1:]:
                docSplitted = docs.split(":")
                if term in self.index:
                    self.index[term][docSplitted[0]] = docSplitted[1]
                    self.positionIndex[term][docSplitted[0]] = docSplitted[2]
                else:
                    self.index[term] = {docSplitted[0]: docSplitted[1]}
                    self.positionIndex[term] = {
                        docSplitted[0]: docSplitted[2]}
        if self.files == []:
            self.safeTerm = ""
            return True
        self.safeTerm = min(currentTerms)
        return False

    def prepareIndex(self):
        for token, postingList in self.index.items():
            if token <= self.safeTerm:
                for docID, tf in postingList.items():
                    postingList[docID] = 1+math.log10(int(tf))
        for token, postingList in self.index.items():
            if token <= self.safeTerm:
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
            if t > self.safeTerm:
                break
            auxString += t
            for doc, w in docs.items():
                auxString += ";"+doc+":" + \
                    str(w)+":"+str(self.positionIndex[t][doc])
            self.out.write(auxString+"\n")
            auxString = ""
            self.positionIndex = {
                x: self.positionIndex[x] for x in self.positionIndex if x != t}
            idx += 1
        if len(self.index) >= idx+1:
            self.safeTerm = self.index[idx][0]
            self.index = dict(self.index[idx:])
        else:
            self.safeTerm = ""
            self.index = {}


class WeightMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)

    def mergeIndex(self):
        # TODO remove files
        currentTerms = []
        for f in self.files:
            line = f.readline().strip().split(";")
            term = line[0]
            currentTerms.append(term)
            if line == [""]:
                self.files.remove(f)
                continue
            for docs in line[1:]:
                docSplitted = docs.split(":")
                if term in self.index:
                    self.index[term][docSplitted[0]] = docSplitted[1]
                else:
                    self.index[term] = {docSplitted[0]: docSplitted[1]}
        if self.files == []:
            self.safeTerm = ""
            return True
        self.safeTerm = min(currentTerms)
        return False

    def prepareIndex(self):
        for token, postingList in self.index.items():
            if token <= self.safeTerm:
                for docID, tf in postingList.items():
                    postingList[docID] = 1+math.log10(int(tf))
        for token, postingList in self.index.items():
            if token <= self.safeTerm:
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
            if t > self.safeTerm:
                break
            auxString += t
            for doc, w in docs.items():
                auxString += ";"+doc+":" + str(w)
            self.out.write(auxString+"\n")
            auxString = ""
            idx += 1
        if len(self.index) >= idx+1:
            self.safeTerm = self.index[idx][0]
            self.index = dict(self.index[idx:])
        else:
            self.safeTerm = ""
            self.index = {}


class PositionMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)
        self.positionIndex = {}

    def mergeIndex(self):
        # TODO remove files
        currentTerms = []
        for f in self.files:
            line = f.readline().strip().split(";")
            term = line[0]
            currentTerms.append(term)
            if line == [""]:
                self.files.remove(f)
                continue
            for docs in line[1:]:
                docSplitted = docs.split(":")
                if term in self.index:
                    self.index[term][docSplitted[0]] = docSplitted[1]
                    self.positionIndex[term][docSplitted[0]] = docSplitted[2]
                else:
                    self.index[term] = {docSplitted[0]: docSplitted[1]}
                    self.positionIndex[term] = {
                        docSplitted[0]: docSplitted[2]}
        if self.files == []:
            self.safeTerm = ""
            return True
        self.safeTerm = min(currentTerms)
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.index = sorted(self.index.items())
        auxString = ""
        idx = 0
        for t, docs in self.index:
            if t > self.safeTerm:
                break
            auxString += t
            for doc, w in docs.items():
                auxString += ";"+doc+":" + \
                    str(w)+":"+str(self.positionIndex[t][doc])
            self.out.write(auxString+"\n")
            auxString = ""
            self.positionIndex = {
                x: self.positionIndex[x] for x in self.positionIndex if x != t}
            idx += 1
        if len(self.index) >= idx+1:
            self.safeTerm = self.index[idx][0]
            self.index = dict(self.index[idx:])
        else:
            self.safeTerm = ""
            self.index = {}


class SimpleMerger(Merger):
    def __init__(self, filename, intermidiateIndex):
        super().__init__(filename, intermidiateIndex)

    def mergeIndex(self):
        # TODO remove files
        currentTerms = []
        for f in self.files:
            line = f.readline().strip().split(",")
            term = line[0]
            currentTerms.append(term)
            if line == [""]:
                self.files.remove(f)
                continue
            for docs in line[1:]:
                docSplitted = docs.split(":")
                if term in self.index:
                    self.index[term][docSplitted[0]] = docSplitted[1]
                else:
                    self.index[term] = {docSplitted[0]: docSplitted[1]}
        if self.files == []:
            self.safeTerm = ""
            return True
        self.safeTerm = min(currentTerms)
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.index = sorted(self.index.items())
        auxString = ""
        idx = 0
        for t, docs in self.index:
            if t > self.safeTerm:
                break
            auxString += t
            for doc, w in docs.items():
                auxString += ","+doc+":" + str(w)
            self.out.write(auxString+"\n")
            auxString = ""
            idx += 1
        if len(self.index) >= idx+1:
            self.safeTerm = self.index[idx][0]
            self.index = dict(self.index[idx:])
        else:
            self.safeTerm = ""
            self.index = {}
