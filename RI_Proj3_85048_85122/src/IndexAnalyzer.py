"""
.. module:: IndexAnalyzer
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""
import sys

content = {}
highestFrequency = 0
HIGHEST_ELEMENTS = 10
termfreqdict = {}
docfreq = []


def buildDict(outputFileName):
    """
    Reads index output file and builds dictionary with terms as keys and number of occurrences as values

    :param: outputFileName: name of the file to be processed
    :type outputFileName: str

    """
    global highestFrequency
    outputFile = open(outputFileName, "r")
    for line in outputFile:
        elements = line.split(",")
        count = 0
        max_freq = 0
        docfreq.append((len(elements[1:]), elements[0]))
        for e in elements[1:]:
            try:
                aux = e.split(":")
                docID, freq = aux[0], int(aux[1])
                count += freq
                if max_freq < freq:
                    max_freq = freq
            except Exception as ex:
                print(ex)
                sys.exit()
        content[elements[0]] = count

        if max_freq in termfreqdict.keys():
            termfreqdict[max_freq].append(elements[0])
        else:
            termfreqdict[max_freq] = [elements[0]]

        if highestFrequency < count:
            highestFrequency = count


def filterByOccur(n):
    """
    Finds the subset of the dictionary where the values are equal to value passed to the function.

    :param: n: value that the user wants to find
    :type n: str
    :returns: subset of the dictionary that contains the value passed
    :rtype: map<str, int>

    """
    retdict = {}
    for key in content:
        if content[key] == int(n):
            retdict[key] = content[key]
    return retdict


def main(args):
    """
    Function that answers to some of the assignments' questions by calculating some properties of the output files.

    :param: args: the list of arguments passed to the script when executed
    :type args: list<str>

    """

    if len(args) == 0:
        print("Please insert output file name as first argument.")
        return

    outputFileName = args[0]
    documentFrequency = 1 if len(args) == 1 else args[1]

    buildDict(outputFileName)
    # just count the keys to calculate the vocabulary size
    print("\nThe given file contains " +
          str(len(content.keys())) + " unique terms.")

    # retrieve only the keys with the desired document frequency
    terms = list(filterByOccur(documentFrequency).keys())
    terms = sorted(terms)  # sort them alphabetically
    firstTerms = terms[0:10]
    print("\nThe " + str(len(firstTerms)) + " first terms with document frequency of " +
          str(documentFrequency) + " (ordered alphabetically):")
    print(firstTerms[0:10])  # print a maximum of 10 terms

    l = list(set(content.values()))  # [(term,{doc:n_occur})]   # []
    l.sort()
    highestCollectionTerms = []
    # decrease auxFrequency as long as the list of terms with highest frequency isn't long enough (while possible)
    while len(highestCollectionTerms) < HIGHEST_ELEMENTS and l != []:
        ma = l.pop()
        auxList = list(filterByOccur(ma).keys())
        for element in auxList:
            if len(highestCollectionTerms) < HIGHEST_ELEMENTS:
                highestCollectionTerms += [(element, ma)]
    if len(highestCollectionTerms) < HIGHEST_ELEMENTS:
        print("\nThe " + str(len(highestCollectionTerms)) +
              " terms with highest collection frequency:")
    else:
        print("\nThe 10 terms with highest collection frequency:")
    # print a maximum of HIGHEST_ELEMENTS terms
    print(highestCollectionTerms[0:HIGHEST_ELEMENTS])

    l = sorted(termfreqdict.items())
    highestDocumentTerms = []
    count = 0
    while count < HIGHEST_ELEMENTS and l != []:
        highestDocumentTerms += [(l[len(l)-1][1], l[len(l)-1][0])]
        count += len(l[len(l)-1][1])
        l = l[0:-1]

    if count < HIGHEST_ELEMENTS:
        print("\nThe " + count +
              " terms with highest document frequency:")
    else:
        print("\nThe 10 terms with highest term frequency:")
    print(highestDocumentTerms)
    docfreq.sort()
    print("\nThe 10 terms with highest document frequency:")
    print(docfreq[-10:])
    print()


if __name__ == "__main__":
    # bypassing the arguments of the script to the main function
    main(sys.argv[1:])
