"""
.. module:: IndexAnalyzer
    :noindex:
.. moduleauthor:: Filipe Pires [85122] & João Alegria [85048]
"""
import sys

content = {}
highestFrequency = 0
HIGHEST_ELEMENTS = 10


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
        for e in elements[1:]:
            try:
                count += int(e.split(":")[1])
            except Exception:
                print(e+"banana")
                sys.exit()
        content[elements[0]] = count
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


# def partition(terms, low, high):
#     """
#     Auxiliary method for the quicksort algorithm. Acts as a partitioner of the terms and when doing so, also sorts them.

#     :param: terms: list of terms to be sorted
#     :type terms: list<str>
#     :param: low: minimum index that the algorithm must consider
#     :type low: int
#     :param: hight: maximum index that the algorithm must consider
#     :type high: int
#     :returns: the index where the list should be partitioned
#     :rtype: int

#     """
#     i = (low-1)
#     pivot = terms[high]

#     for j in range(low, high):
#         if terms[j] <= pivot:
#             i += 1
#             terms[i], terms[j] = terms[j], terms[i]

#     terms[i+1], terms[high] = terms[high], terms[i+1]
#     return (i+1)


# def quicksortAlphabetical(terms):
#     """
#     Quicksort algorithm implementation that orders the passed terms alphabetically.

#     :param: terms: list of terms to be sorted
#     :type terms: list<str>

#     """
#     if len(terms) <= 1:
#         return terms
#     pi = terms[0]
#     greater = [x for x in terms[1:] if x >= pi]
#     less = [x for x in terms[1:] if x < pi]
#     return quicksortAlphabetical(less)+[pi]+quicksortAlphabetical(greater)


def main(args):
    """
    Function that answerers to some of the assignment's questions. Function that creates the data flow for the auxiliar script.

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

    l = list(set(content.values()))
    l.sort()
    highestTerms = []
    # decrease auxFrequency as long as the list of terms with highest frequency isn't long enough (while possible)
    while len(highestTerms) < HIGHEST_ELEMENTS and l != []:
        ma = l.pop()
        auxList = list(filterByOccur(ma).keys())
        for element in auxList:
            if len(highestTerms) < HIGHEST_ELEMENTS:
                highestTerms += [(element, ma)]
    if len(highestTerms) < 10:
        print("\nThe " + str(len(highestTerms)) +
              " terms with highest document frequency:")
    else:
        print("\nThe 10 terms with highest document frequency:")
    print(highestTerms[0:10])  # print a maximum of 10 terms
    print()


if __name__ == "__main__":
    # bypassing the arguments of the script to the main function
    main(sys.argv[1:])
