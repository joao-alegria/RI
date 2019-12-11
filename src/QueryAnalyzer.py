"""
.. module:: QueryAnalyzer
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & Joao Alegria [85048]
"""

import sys
import os
import math


def loadQueryTruth(queryTruth):
    """
    Processes the gold standard file.

    :param queryTruth: filename of the gold standard
    :type queryTruth: str
    """

    f = open(queryTruth)
    queryResults = {}
    for line in f:
        processedLine = line.strip().split("\t")
        if processedLine[0] not in queryResults:
            queryResults[processedLine[0]] = [processedLine[1:]]
        else:
            queryResults[processedLine[0]].append(processedLine[1:])
    return queryResults


def loadOurResults(ourQuery):
    """
    Processes the various query result files.

    :param ourQuery: filename of the query results
    :type ourQuery: str
    """

    f = open(ourQuery)
    ourResults = []
    for line in f:
        processedLine = line.strip().split(",")[0]
        if processedLine not in ourResults:
            ourResults.append(processedLine)

    return ourResults


def calculateP_R_F1(truth, prediction):
    """
    Calculates the Precision, Recall and F-Measure of a given query result.

    :param truth: list of gold standard documents
    :type truth: list<str>
    :param prediction: list of our system returned results
    :type prediction: list<str>
    """

    tp = 0
    fp = 0
    fn = 0
    for p in prediction:
        if p in truth:
            tp += 1
        else:
            fp += 1
    for t in truth:
        if t not in prediction:
            fn += 1
    P = tp/(tp+fp) if (tp+fp) != 0 else 0.0
    R = tp/(tp+fn) if (tp+fn) != 0 else 0.0
    F1 = (2*R*P)/(R+P) if (R+P) != 0 else 0.0

    return P, R, F1


def calculateMPatK(truth, prediction, k):
    """
    Calculates the Mean Precision on a given rank of the results.

    :param truth: list of gold standard documents
    :type truth: list<str>
    :param prediction: list of our system returned results
    :type prediction: list<str>
    :param k: rank at which the mean precision should be calculated at
    :type k: int
    """

    pSum = 0
    count = 0
    for idx, p in enumerate(prediction[:k]):
        if p in truth:
            count += 1
            P, R, F1 = calculateP_R_F1(truth, prediction[:idx])
            pSum += P
    return pSum/count if count != 0 else 0.0


def calculateNDCG(truth, prediction):
    """
    Calculates the Normalized Discounted Cumulative Gain.

    :param truth: list of gold standard documents and its relevance
    :type truth: list<tup<str,int>>
    :param prediction: list of our system returned results
    :type prediction: list<str>
    """
    ideal = 0
    actual = 0
    predictionRelevance = []
    for p in prediction:
        wrote = False
        for t, tv in truth:
            if p == t:
                wrote = True
                predictionRelevance.append(tv)
        if not wrote:
            predictionRelevance.append(0)

    # idealRelevance = [x[1] for x in truth]
    idealRelevance = predictionRelevance.copy()
    idealRelevance.sort(reverse=True)
    for idx in range(len(idealRelevance)):
        denominator = math.log2(idx+1) if idx+1 > 1 else 1
        actual += predictionRelevance[idx]/denominator
        ideal += idealRelevance[idx]/denominator
    return actual/ideal if ideal != 0 else 0.0


def main(argv):
    if len(argv) != 3:
        print("""USAGE:
        python3 QueryAnalyzer.py <queryTruth> <queryResultFolder> <outputFile>
        """)
        sys.exit(0)
    queryTruth = argv[0]
    ourResultsFolder = argv[1]
    outputFilename = argv[2]

    queryTrueResults = loadQueryTruth(queryTruth)

    ourResults = os.listdir(ourResultsFolder)
    mps = []
    precisions = []
    recalls = []
    f1s = []
    mpat10s = []
    ndcgs = []

    outFile = open(outputFilename, "w")
    outFile.write(
        "Query, Precision, Recall, F1, MeanPrecision, MeanPrecision@10, NDCG\n")
    for f in ourResults:
        truth = queryTrueResults[f]
        trueDocs = [x[0] for x in truth]
        results = loadOurResults(ourResultsFolder+"/"+f)
        P, R, F1 = calculateP_R_F1(trueDocs, results)
        mpat10 = calculateMPatK(trueDocs, results, 10)
        ndcg = calculateNDCG([[x[0], int(x[1])] for x in truth], results)
        mp = calculateMPatK(trueDocs, results, len(results))
        mps.append(mp)
        precisions.append(P)
        recalls.append(R)
        f1s.append(F1)
        mpat10s.append(mpat10)
        ndcgs.append(ndcg)
        outFile.write("{},{},{},{},{},{},{}\n".format(
            f, P, R, F1, mp, mpat10, ndcg))

    aP = sum(precisions)/len(precisions)
    aR = sum(recalls)/len(recalls)
    aF1 = sum(f1s)/len(f1s)
    aMP = sum(mps)/len(mps)
    aMP10 = sum(mpat10s)/len(mpat10s)
    aNDCG = sum(ndcgs)/len(ndcgs)

    outFile.write("{},{},{},{},{},{},{}\n".format(
        "Avg", aP, aR, aF1, aMP, aMP10, aNDCG))


if __name__ == "__main__":
    main(sys.argv[1:])
