
# Authors: Filipe Pires [85122] & João Alegria [85048]

import re
from abc import ABC, abstractmethod

# Class responsible for parsing input files

class FileParser:
    def __init__(self, files, limit):
        self.content = {}
        self.files = files
        self.limit = limit

    def getContent(self):
        for filename in self.files:
            f = open(filename, "r")
            docID = ""
            docContent = ""

            if self.limit == None:
                for x in f:
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
                            if docContent != "": # detects the end of titles with 2+ lines
                                self.content[docID] = docContent
                                docID = ""
                                docContent = ""
                            else:
                                continue
                    else:
                        if docContent != "":
                            docContent += " "+label # in this case label=title content
                f.close()
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
                                # to do: consider that the file already exists and that we are reading it a second time
                                # or leave it this way since we do not allow duplications
                                self.content[docID] = docContent
                                docID = ""
                                docContent = ""
                            else:
                                continue
                    else:
                        if docContent != "":
                            docContent += " "+label
                f.close()

