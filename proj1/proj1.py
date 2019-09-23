import re
from abc import ABC, abstractmethod


class FileParser:
    def __init__(self, filename, limit):
        self.content = {}
        self.filename = filename
        self.limit = limit

    def getContent(self):
        f = open(self.filename, "r")
        docID = ""
        docContent = ""

        if self.limit == 0:
            # for x in f:
            #     line = f.readline()
            #     if line == "":
            #         break
            #     splittedLine = line.strip().split("-")
            #     label = splittedLine[0].strip()
            #     if(len(splittedLine) >= 2):
            #         content = splittedLine[1].strip()
            #         if label == "PMID":
            #             docID = content
            #         elif label == "TI":
            #             if docID != "":
            #                 docContent = content
            #         else:
            #             if docContent != "":
            #                 self.content[docID] = docContent
            #                 docID = ""
            #                 docContent = ""
            #             else:
            #                 continue
            #     else:
            #         if docContent != "":
            #             docContent += " "+label
            pass
        else:
            for x in range(self.limit):
                line = f.readline()
                if line == "":
                    break
                splittedLine = line.strip().split("-")
                label = splittedLine[0].strip()
                if(len(splittedLine) >= 2):
                    content = splittedLine[1].strip()
                    if label == "PMID":
                        docID = content
                    elif label == "TI":
                        if docID != "":
                            docContent = content
                    else:
                        if docContent != "":
                            self.content[docID] = docContent
                            docID = ""
                            docContent = ""
                        else:
                            continue
                else:
                    if docContent != "":
                        docContent += " "+label
            f.close()


class Tokenizer(ABC):
    def __init__(self, content):
        self.tokens = {}
        self.content = content
        super().__init__()

    @abstractmethod
    def tokenize(self):
        print("Processing...")
        pass


class SimpleTokenizer(Tokenizer):
    def tokenize(self):
        super().tokenize()
        for docID, docContent in self.content.items():
            normalizeData = re.sub("[^a-zA-Z]+", " ", docContent).lower()
            token = normalizeData.split(" ")
            for t in token:
                if t not in self.tokens:
                    self.tokens[t] = {docID: 1}
                else:
                    if docID not in self.tokens[t]:
                        self.tokens[t][docID] = 1
                    else:
                        self.tokens[t][docID] = self.tokens[t][docID]+1


class ComplexTokenizer(Tokenizer):
    def __init__(self, content):
        self.tokens = {}
        self.content = content

    def tokenize(self):
        super().tokenize()
        pass


class PersistIndex(ABC):

    def __init__(self, content, filename):
        self.content = content
        self.filename = filename
        super().__init__()

    @abstractmethod
    def persist(self):
        print("Persisting...")


class PersistCSV(PersistIndex):
    def persist(self):
        super().persist()
        f = open(self.filename, "w")
        for token, freqs in self.content.items():
            f.write(token)
            for docID, count in freqs.items():
                f.write(",")
                f.write(docID+":"+str(count))
            f.write("\n")
        f.close()


fp = FileParser("2004_TREC_ASCII_MEDLINE_1", 300)
fp.getContent()
t = SimpleTokenizer(fp.content)
t.tokenize()
PersistCSV(t.tokens, "out.txt").persist()
