import io
import os
import math
from abc import ABC, abstractmethod
from decimal import *

getcontext().prec = 2


class Merger(ABC):
    def __init__(self, intermidiateIndex, indexer):
        # self.out = open(filename, "w")
        self.outDir = "index/"
        if not os.path.exists(self.outDir):
            os.makedirs(self.outDir)
        else:
            for f in [f for f in os.listdir("index/")]:
                os.remove("index/"+f)
        self.files = [io.open(x, "r") for x in intermidiateIndex]
        self.index = []
        self.indexer = indexer

    @abstractmethod
    def mergeIndex(self):
        return True

    @abstractmethod
    def writeIndex(self):
        pass

    def clearVar(self):
        pass


class PositionWeightMerger(Merger):
    def __init__(self, intermidiateIndex, indexer):
        super().__init__(intermidiateIndex, indexer)
        self.terms = [x.readline().strip().split(";") for x in self.files]

    def mergeIndex(self):
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
        docs = []
        for idx, t in enumerate(self.terms):
            if term == t[0][:t[0].find(":")]:
                docs += t[1:]
                self.terms[idx] = ""

        self.index.append((term, {}))
        for d in docs:
            self.index[-1][1][d.split(":")
                              [0]] = d.split(":")[2].split(",")
        docs = []
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        out = open(self.outDir+self.index[0][0]+"_"+self.index[-1][0], "w")
        auxString = ""
        for t, docs in self.index:
            idf, w2 = self.indexer.normalize(docs)
            auxString += t+":"+str(idf)
            for doc, w in docs.items():
                auxString += ";"+doc+":" + \
                    str(w2[0])+":" + \
                    str(w[0])+"".join(","+str(x) for x in w[1:])
                w2 = w2[1:]
            out.write(auxString+"\n")
            auxString = ""
        self.index = []
        out.close()


class WeightMerger(Merger):
    def __init__(self, intermidiateIndex, indexer):
        super().__init__(intermidiateIndex, indexer)
        self.terms = [x.readline().strip().split(";") for x in self.files]

    def mergeIndex(self):
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
        docs = []
        for idx, t in enumerate(self.terms):
            if term == t[0][:t[0].find(":")]:
                docs += t[1:]
                self.terms[idx] = ""

        self.index.append((term, {}))
        for d in docs:
            self.index[-1][1][d.split(":")[0]] = d.split(":")[1]
        docs = []
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        out = open(self.outDir+self.index[0][0]+"_"+self.index[-1][0], "w")
        auxString = ""
        for t, docs in self.index:
            idf, w2 = self.indexer.normalize(docs)
            auxString += t+":"+str(idf)
            for doc, w in docs.items():
                auxString += ";"+doc+":" + str(w2[0])
                w2 = w2[1:]
            out.write(auxString+"\n")
            auxString = ""
        self.index = []
        out.close()


class PositionMerger(Merger):
    def __init__(self, intermidiateIndex, indexer):
        super().__init__(intermidiateIndex, indexer)
        self.positionIndex = {}
        self.terms = [x.readline().strip().split(";") for x in self.files]

    def mergeIndex(self):
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
        docs = []
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                docs += t[1:]
                self.terms[idx] = ""

        self.index.append((term, {}))
        for d in docs:
            self.index[-1][1][d.split(":")
                              [0]] = d.split(":")[2].split(",")
        docs = []
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        out = open(self.outDir+self.index[0][0]+"_"+self.index[-1][0], "w")
        auxString = ""
        for t, docs in self.index:
            auxString += t
            for doc, w in docs.items():
                auxString += ";"+doc+":" + \
                    str(len(w))+":" + \
                    str(w[0])+"".join(","+str(x) for x in w[1:])
            out.write(auxString+"\n")
            auxString = ""
        self.index = []
        out.close()


class SimpleMerger(Merger):
    def __init__(self, intermidiateIndex, indexer):
        super().__init__(intermidiateIndex, indexer)
        self.terms = [x.readline().strip().split(",") for x in self.files]

    def mergeIndex(self):
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
        docs = []
        for idx, t in enumerate(self.terms):
            if t[0] == term:
                docs += t[1:]
                self.terms[idx] = ""

        self.index.append((term, {}))
        for d in docs:
            self.index[-1][1][d.split(":")[0]] = d.split(":")[1]
        docs = []
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.index == []:
            return
        self.index.sort(key=lambda tup: tup[0])
        out = open(self.outDir+self.index[0][0]+"_"+self.index[-1][0], "w")
        auxString = ""
        for t, docs in self.index:
            auxString += t
            for doc, w in docs.items():
                auxString += ","+doc+":" + str(w)
            out.write(auxString+"\n")
            auxString = ""
        self.index = []
        out.close()
