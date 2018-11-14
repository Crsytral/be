import csv
import codecs
from collections import Counter

from models import Author, Submission, Review
from utils import parseCSVFile, testCSVFileFormatMatching, isNumber, parseSubmissionTime

def parseAuthorCSVFile(inputFile):

    csvFile = inputFile
    dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvFile, "utf-8").read(1024))
    csvFile.open()
    # reader = csv.reader(codecs.EncodedFile(csvFile, "utf-8"), delimiter=',', dialect=dialect)
    reader = csv.reader(codecs.EncodedFile(csvFile, "utf-8"), delimiter=',', dialect='excel')

    rowResults = []
    for index, row in enumerate(reader):
        rowResults.append(row)
        print(row)
        print(type(row))
        if index == 5:
            break

    parsedResult = {}

    return parsedResult

def getAuthorInfo(inputFile):
    """
    author.csv: header row, author names with affiliations, countries, emails
    data format:
    submission ID | f name | s name | email | country | affiliation | page | person ID | corresponding?
    """
    author = Author(inputFile)
    return author.getAuthorInfo()

def getReviewScoreInfo(inputFile):
    """
    review_score.csv
    data format:
    review ID | field ID | score
    File has header

    e.g. 1,1,3 - score (can be negative)
         1,2,5 - confidence
         1,3,no - recommended
    """
    parsedResult = {}
    lines = parseCSVFile(inputFile)[1:]
    lines = [ele for ele in lines if ele]
    scores = []
    confidences = []
    isRecommended = []

    scores = [int(line[2]) for line in lines if int(line[1]) == 1]
    confidences = [int(line[2]) for line in lines if int(line[1]) == 2]
    isRecommended = [str(line[2]).replace("\r", "") for line in lines if int(line[1]) == 3]

    parsedResult['yesPercentage'] = float(isRecommended.count('yes')) / len(isRecommended)
    parsedResult['meanScore'] = sum(scores) / float(len(scores))
    parsedResult['meanConfidence'] = sum(confidences) / float(len(confidences))
    parsedResult['totalReview'] = len(confidences)

    return {'infoType': 'reviewScore', 'infoData': parsedResult}

def getReviewInfo(inputFile):
    """
    review.csv
    data format:
    review ID | paper ID? | reviewer ID | reviewer name | unknown | text | scores | overall score | unknown | unknown | unknown | unknown | date | time | recommend?
    File has NO header

    score calculation principles:
    Weighted Average of the scores, using reviewer's confidence as the weights

    recommended principles:
    Yes: 1; No: 0; weighted average of the 1 and 0's, also using reviewer's confidence as the weights
    """
    review = Review(inputFile)
    return review.getReviewInfo()


def getSubmissionInfo(inputFile):
    """
    submission.csv
    data format:
    submission ID | track ID | track name | title | authors | submit time | last update time | form fields | keywords | decision | notified | reviews sent | abstract
    File has header
    """
    submission = Submission(inputFile)
    return submission.getSubmissionInfo()


def getAuthorAndSubmissionInfo(listOfFiles):
    for csvFile in listOfFiles:
        if str(csvFile.name) == "author.csv":
            authorFile = csvFile
        else:
            submissionFile = csvFile

    # Set up individual file objects
    author = Author(authorFile)
    submission = Submission(submissionFile)
    parsedResult = {}

    # Handling combination
    authorList = []
    for submissionInfo in submission.lines:
        for authorInfo in author.lines:
            if str(submissionInfo[9]) == 'accept' and str(authorInfo[0]) == str(submissionInfo[0]):
                authorList.append({'name': authorInfo[1] + " " + authorInfo[2], 'country': authorInfo[4], 'affiliation': authorInfo[5]})

    # Computation of results
    countries = [ele['country'] for ele in authorList if ele]
    topCountries = Counter(countries).most_common(10)
    parsedResult['topAcceptedCountries'] = {'labels': [ele[0] for ele in topCountries],
                                    'data': [ele[1] for ele in topCountries]}

    affiliations = [ele['affiliation'] for ele in authorList if ele]
    topAffiliations = Counter(affiliations).most_common(10)
    parsedResult['topAcceptedAffiliations'] = {'labels': [ele[0] for ele in topAffiliations],
                                       'data': [ele[1] for ele in topAffiliations]}

    topCountriesLabel = [ele[0] for ele in topCountries]
    topCountriesKeywordDict = dict((el, []) for el in topCountriesLabel)
    for submissionInfo in submission.lines:
        for authorInfo in author.lines:
            # Check that submission # are equal, then check author's country is in topCountries
            if str(authorInfo[0]) == str(submissionInfo[0]) and authorInfo[4] in topCountriesLabel:
                allKeywords = str(submissionInfo[8]).lower().replace("\r", "").split("\n")
                topCountriesKeywordDict[authorInfo[4]].extend(allKeywords)

    # Different format to match requirements by client
    headerArr = ["countries", "keyword", "count"]
    topCountryKeywordArr = []
    topCountryKeywordArr.append(headerArr)
    for country in topCountriesLabel:
        temp = Counter(topCountriesKeywordDict[country]).most_common(1)
        arr = [country, temp[0][0], temp[0][1]]
        topCountryKeywordArr.append(arr)

    parsedResult['topCountryKeyword'] = [topCountryKeywordArr]

    # Merge all data into one dict
    # finalResults = merge_two_dicts(authorResult, parsedResult)
    # finalResults = merge_two_dicts(finalResults, submissionResult)
    return {'infoType': 'authorAndSubmission', 'infoData': parsedResult}


def getAuthorAndReviewInfo(listOfFiles):
    for csvFile in listOfFiles:
        if str(csvFile.name) == "author.csv":
            authorFile = csvFile
        else:
            reviewFile = csvFile

    author = Author(authorFile)
    review = Review(reviewFile)
    parsedResult = {}

    # Handling combination
    authorList = [] # Stores the data that satisfies the criteria
    # only include with the paper is recommended
    for reviewInfo in review.lines:
        for authorInfo in author.lines:
            # Check if reviewer recommends the paper for best paper and submission# is same
            if str(reviewInfo[14]) == 'yes' and str(authorInfo[0]) == str(reviewInfo[1]):
                authorList.append({'name': authorInfo[1] + " " + authorInfo[2], 'country': authorInfo[4], 'affiliation': authorInfo[5]})

    # Computation of merged results
    countries = [ele['country'] for ele in authorList if ele]
    topCountries = Counter(countries).most_common(10)
    parsedResult['topBestPPCountries'] = {'labels': [ele[0] for ele in topCountries],
                                    'data': [ele[1] for ele in topCountries]}

    affiliations = [ele['affiliation'] for ele in authorList if ele]
    topAffiliations = Counter(affiliations).most_common(10)
    parsedResult['topBestPPAffiliations'] = {'labels': [ele[0] for ele in topAffiliations],
                                       'data': [ele[1] for ele in topAffiliations]}

    return {'infoType': 'authorAndReview', 'infoData': parsedResult}


def invalidFiles():
    return {'infoType': 'invalidFiles', 'infoData': {}}


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


if __name__ == "__main__":
    parseCSVFile(fileName)