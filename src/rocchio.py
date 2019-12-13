"""
.. module:: Rocchio Auxiliary Script
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""

import os
import sys
import psutil
import gc
import getopt

import Tokenizer
import Searcher

inputFolder = "../index/"
inputFiles = os.listdir(inputFolder)
tokenizer = Tokenizer.ComplexTokenizer()
limit = 20
maximumRAM = None
feedback = "user" #None
N = [5, 10, 20]
k = 10000
rocchioWeights = [1.0, 1.0, 0.1] #[]

for n in N:
    queriesFile = open("../queries.txt", "r")
    pseudoFeedbackFile = open("../pseudoFeedback/"+str(n)+".txt", "w")
    userFeedbackFile = open("../userFeedback/"+str(n)+".txt", "w")

    for line in queriesFile:
        # process each query
        query = line.split("\t")
        searcher = Searcher.IndexSearcher(
            tokenizer, limit, inputFolder, maximumRAM, feedback, n, k, rocchioWeights)
        searcher.retrieveRequiredFiles(query[1])

        searcher.calculateScores()
        scores = sorted(searcher.scores.items(),
                        key=lambda kv: kv[1], reverse=True)

        requiredFiles = []
        for term in searcher.tokenizer.tokens:
            for f in inputFiles:
                aux = f.split("_")
                if term > aux[0] and term < aux[1]:
                    if f not in requiredFiles:
                        requiredFiles.append(f)
                        break

        # pseudo feedback
        relevantDocs = []
        relevantSumDj = 0.0
        for element in scores[:n]:
            relevantDocs.append(str(element[0]))

        # irrelevantDocs = []
        # irrelevantSumDj = 0.0
        # for element in scores[n:]:
        #    irrelevantDocs.append(str(element[0]))

        for file in requiredFiles:
            f = open(inputFolder+file)
            for l in f:
                if l.split(":")[0] in searcher.tokenizer.tokens:
                    content = l.strip().split(";")[1:]
                    for c in content:
                        c = c.split(":")
                        if c[0] in relevantDocs:
                            relevantSumDj += float(c[1])
                        # elif content[i][0] in irrelevantDocs:
                        #     irrelevantSumDj += float(content[i][1])
            f.close()
        relevantSumDj = round(relevantSumDj, 2)
        #irrelevantSumDj = round(irrelevantSumDj, 2)
        # + ":" + str(len(irrelevantDocs)) + ":" + str(irrelevantSumDj) + "\n")
        pseudoFeedbackFile.write(
            str(query[0]) + ":" + str(len(relevantDocs)) + ":" + str(relevantSumDj) + "\n")

        # user feedback
        gold = {}
        for standard in open("../queries.relevance.txt"):
            line = standard.strip().split("\t")
            if line[0] not in gold:
                gold[line[0]] = [line[1]]
            else:
                gold[line[0]].append(line[1])

        translationFile = open("../indexMetadata.txt")
        translations = []
        for line in translationFile:
            line = line.strip().split(",")
            translations.append(int(line[1]))
        relevantDocs = []
        relevantSumDj = 0.0
        irrelevantDocs = []
        irrelevantSumDj = 0.0
        i = 0
        for element in scores:
            if i >= n:
                break
            # if current line in gold standard regards current query
            if str(element[0]) in gold[query[0]]:
                relevantDocs.append(str(element[0]))
                i += 1
            else:
                irrelevantDocs.append(str(element[0]))
                i += 1

        for file in requiredFiles:
            f = open(inputFolder+file)
            for l in f:
                if l.split(":")[0] in searcher.tokenizer.tokens:
                    content = l.strip().split(";")[1:]
                    for c in content:
                        c = c.split(":")
                        if str(translations[int(c[0])-1]) in relevantDocs:
                            relevantSumDj += float(c[1])
                        if str(translations[int(c[0])-1]) in irrelevantDocs:
                            irrelevantSumDj += float(c[1])
            f.close()
        relevantSumDj = round(relevantSumDj, 2)
        irrelevantSumDj = round(irrelevantSumDj, 2)
        userFeedbackFile.write(str(query[0]) + ":" + str(len(relevantDocs)) + ":" + str(
            relevantSumDj) + ":" + str(len(irrelevantDocs)) + ":" + str(irrelevantSumDj) + "\n")

        # relevantDocs = ""
        # irrelevantDocs = ""
        # for element in scores[:n]:
        #     relevantDocs += str(element[0]) + ","
        # pseudoFeedbackFile.write(str(query[0]) + ":" + str(n) + ":" + relevantDocs + "\n")

        # relevantDocs = ""
        # irrelevantDocs = ""
        # i=0
        # for element in scores:
        #     contains = False
        #     goldStandardFile = open("../queries.relevance.txt", "r")
        #     for l in goldStandardFile:
        #         content = l.split("\t")
        #         if int(content[0])==int(query[0]): # if current line in gold standard regards current query
        #             if int(content[1])==int(element[0]): # if current score element
        #                 relevantDocs += str(element[0]) + ","
        #                 i += 1
        #                 contains = True
        #                 break
        #     if not contains:
        #         irrelevantDocs += str(element[0]) + ","
        #         i += 1
        #     if i>=n:
        #         break
        # userFeedbackFile.write(str(query[0]) + ":" + relevantDocs + ":" + irrelevantDocs + "\n")

    pseudoFeedbackFile.close()
    userFeedbackFile.close()
