import io


class Merger():
    def __init__(self, filename, intermidiateIndex):
        self.out = open(filename, "w")
        self.files = [io.open(x, "r") for x in intermidiateIndex]
        self.safeTerm = ""
        self.terms = {}

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
            if term in self.terms:
                self.terms[term] += line[1:]
            else:
                self.terms[term] = line[1:]
        if self.files == []:
            self.safeTerm = ""
            return True
        minTerm = min(currentTerms)
        if minTerm > self.safeTerm:
            self.safeTerm = minTerm
        return False

    def writeIndex(self):
        # TODO: maybe losing info!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        sortedTerms = sorted(self.terms.items())
        auxString = ""
        for t, docs in sortedTerms:
            if t == self.safeTerm:
                break
            auxString += t
            for doc in docs:
                auxString += ";"+doc
            self.out.write(auxString+"\n")
            auxString = ""
        self.safeTerm = ""
        self.terms = {}
        sortedTerms = []


# merge without restrictions
# def mergeIndex(self, intermidiateIndex):
#     # TODO: when reached ram total + remove files
#     safeIdx = 0

#     files = [io.open(x, "r") for x in intermidiateIndex]
#     line = files[0].readline().strip().split(";")

#     terms = {line[0]: line[1:]}
#     while files != []:
#         for f in files:
#             line = f.readline().strip().split(";")
#             if line == [""]:
#                 files.remove(f)
#                 continue
#             if line[0] in terms:
#                 terms[line[0]] += line[1:]
#             else:
#                 terms[line[0]] = line[1:]
#         safeIdx += 1

#     out = open(self.filename, "w")
#     auxString = ""
#     for t, docs in sorted(terms.items()):
#         auxString += t
#         for doc in docs:
#             auxString += ";"+doc
#         out.write(auxString+"\n")
#         auxString = ""
