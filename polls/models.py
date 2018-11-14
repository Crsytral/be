# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from utils import parseCSVFile, parseSubmissionTime
from collections import Counter

class Author:
  def __init__(self, inputFile):

    lines = parseCSVFile(inputFile)[1:]
    self.lines = [ele for ele in lines if ele]
    authorList = []

    for authorInfo in lines:
        # authorInfo = line.replace("\"", "").split(",")
        # print authorInfo
        authorList.append({'name': authorInfo[1] + " " + authorInfo[2], 'country': authorInfo[4], 'affiliation': authorInfo[5]})

    authors = [ele['name'] for ele in authorList if ele] # adding in the if ele in case of empty strings; same applies below
    self.topAuthors = Counter(authors).most_common(10)

    countries = [ele['country'] for ele in authorList if ele]
    self.topCountries = Counter(countries).most_common(10)

    affiliations = [ele['affiliation'] for ele in authorList if ele]
    self.topAffiliations = Counter(affiliations).most_common(10)

  def getAuthorInfo(self):
    parsedResult = {}
    parsedResult['topAuthors'] = {'labels': [ele[0] for ele in self.topAuthors], 'data': [ele[1] for ele in self.topAuthors]}
    parsedResult['topCountries'] = {'labels': [ele[0] for ele in self.topCountries], 'data': [ele[1] for ele in self.topCountries]}
    parsedResult['topAffiliations'] = {'labels': [ele[0] for ele in self.topAffiliations], 'data': [ele[1] for ele in self.topAffiliations]}
    return {'infoType': 'author', 'infoData': parsedResult}

class Submission:
    def __init__(self, inputFile):
        lines = parseCSVFile(inputFile)[1:]
        self.lines = [ele for ele in lines if ele]
        acceptedSubmission = [line for line in lines if str(line[9]) == 'accept']
        rejectedSubmission = [line for line in lines if str(line[9]) == 'reject']

        self.acceptanceRate = float(len(acceptedSubmission)) / len(lines)

        submissionTimes = [parseSubmissionTime(str(ele[5])) for ele in lines]
        lastEditTimes = [parseSubmissionTime(str(ele[6])) for ele in lines]
        submissionTimes = Counter(submissionTimes)
        lastEditTimes = Counter(lastEditTimes)
        timeStamps = sorted([k for k in submissionTimes])
        lastEditStamps = sorted([k for k in lastEditTimes])
        submittedNumber = [0 for n in range(len(timeStamps))]
        lastEditNumber = [0 for n in range(len(lastEditStamps))]
        self.timeSeries = []
        self.lastEditSeries = []
        for index, timeStamp in enumerate(timeStamps):
            if index == 0:
                submittedNumber[index] = submissionTimes[timeStamp]
            else:
                submittedNumber[index] = submissionTimes[timeStamp] + submittedNumber[index - 1]

            self.timeSeries.append({'x': timeStamp, 'y': submittedNumber[index]})

        for index, lastEditStamp in enumerate(lastEditStamps):
            if index == 0:
                lastEditNumber[index] = lastEditTimes[lastEditStamp]
            else:
                lastEditNumber[index] = lastEditTimes[lastEditStamp] + lastEditNumber[index - 1]

            self.lastEditSeries.append({'x': lastEditStamp, 'y': lastEditNumber[index]})

        # timeSeries = {'time': timeStamps, 'number': submittedNumber}
        # lastEditSeries = {'time': lastEditStamps, 'number': lastEditNumber}

        acceptedKeywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in acceptedSubmission]
        acceptedKeywords = [ele for item in acceptedKeywords for ele in item]
        self.acceptedKeywordMap = {k: v for k, v in Counter(acceptedKeywords).iteritems()}
        self.acceptedKeywordList = [[ele[0], ele[1]] for ele in Counter(acceptedKeywords).most_common(20)]

        rejectedKeywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in rejectedSubmission]
        rejectedKeywords = [ele for item in rejectedKeywords for ele in item]
        self.rejectedKeywordMap = {k: v for k, v in Counter(rejectedKeywords).iteritems()}
        self.rejectedKeywordList = [[ele[0], ele[1]] for ele in Counter(rejectedKeywords).most_common(20)]

        allKeywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in lines]
        allKeywords = [ele for item in allKeywords for ele in item]
        self.allKeywordMap = {k: v for k, v in Counter(allKeywords).iteritems()}
        self.allKeywordList = [[ele[0], ele[1]] for ele in Counter(allKeywords).most_common(20)]

        tracks = set([str(ele[2]) for ele in lines])
        paperGroupsByTrack = {track: [line for line in lines if str(line[2]) == track] for track in tracks}
        self.keywordsGroupByTrack = {}
        self.acceptanceRateByTrack = {}
        self.comparableAcceptanceRate = {}
        self.topAuthorsByTrack = {}

        # Obtained from the JCDL.org website: past conferences
        self.comparableAcceptanceRate['year'] = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
        self.comparableAcceptanceRate['Full Papers'] = [0.29, 0.28, 0.27, 0.29, 0.29, 0.30, 0.29, 0.30]
        self.comparableAcceptanceRate['Short Papers'] = [0.29, 0.37, 0.31, 0.31, 0.32, 0.50, 0.35, 0.32]
        for track, papers in paperGroupsByTrack.iteritems():
            keywords = [str(ele[8]).lower().replace("\r", "").split("\n") for ele in papers]
            keywords = [ele for item in keywords for ele in item]
            # keywordMap = {k : v for k, v in Counter(keywords).iteritems()}
            keywordMap = [[ele[0], ele[1]] for ele in Counter(keywords).most_common(20)]
            self.keywordsGroupByTrack[track] = keywordMap

            acceptedPapersPerTrack = [ele for ele in papers if str(ele[9]) == 'accept']
            self.acceptanceRateByTrack[track] = float(len(acceptedPapersPerTrack)) / len(papers)

            acceptedPapersThisTrack = [paper for paper in papers if str(paper[9]) == 'accept']
            acceptedAuthorsThisTrack = [str(ele[4]).replace(" and ", ", ").split(", ") for ele in
                                        acceptedPapersThisTrack]
            acceptedAuthorsThisTrack = [ele for item in acceptedAuthorsThisTrack for ele in item]
            topAcceptedAuthorsThisTrack = Counter(acceptedAuthorsThisTrack).most_common(10)
            self.topAuthorsByTrack[track] = {'names': [ele[0] for ele in topAcceptedAuthorsThisTrack],
                                        'counts': [ele[1] for ele in topAcceptedAuthorsThisTrack]}

            if track == "Full Papers" or track == "Short Papers":
                self.comparableAcceptanceRate[track].append(float(len(acceptedPapersPerTrack)) / len(papers))

        acceptedAuthors = [str(ele[4]).replace(" and ", ", ").split(", ") for ele in acceptedSubmission]
        acceptedAuthors = [ele for item in acceptedAuthors for ele in item]
        topAcceptedAuthors = Counter(acceptedAuthors).most_common(10)
        self.topAcceptedAuthorsMap = {'names': [ele[0] for ele in topAcceptedAuthors],
                                 'counts': [ele[1] for ele in topAcceptedAuthors]}
        # topAcceptedAuthors = {ele[0] : ele[1] for ele in Counter(acceptedAuthors).most_common(10)}


    def getSubmissionInfo(self):
        parsedResult = {}
        parsedResult['acceptanceRate'] = self.acceptanceRate
        parsedResult['overallKeywordMap'] = self.allKeywordMap
        parsedResult['overallKeywordList'] = self.allKeywordList
        parsedResult['acceptedKeywordMap'] = self.acceptedKeywordMap
        parsedResult['acceptedKeywordList'] = self.acceptedKeywordList
        parsedResult['rejectedKeywordMap'] = self.rejectedKeywordMap
        parsedResult['rejectedKeywordList'] = self.rejectedKeywordList
        parsedResult['keywordsByTrack'] = self.keywordsGroupByTrack
        parsedResult['acceptanceRateByTrack'] = self.acceptanceRateByTrack
        parsedResult['topAcceptedAuthors'] = self.topAcceptedAuthorsMap
        parsedResult['topAuthorsByTrack'] = self.topAuthorsByTrack
        parsedResult['timeSeries'] = self.timeSeries
        parsedResult['lastEditSeries'] = self.lastEditSeries
        parsedResult['comparableAcceptanceRate'] = self.comparableAcceptanceRate
        return {'infoType': 'submission', 'infoData': parsedResult}


class Review:
    def __init__(self, inputFile):

        lines = parseCSVFile(inputFile)
        self.lines = [ele for ele in lines if ele]
        evaluation = [str(line[6]).replace("\r", "") for line in lines]
        submissionIDs = set([str(line[1]) for line in lines])

        self.scoreList = []
        self.recommendList = []
        self.confidenceList = []

        self.submissionIDReviewMap = {}

        # Idea: from -3 to 3 (min to max scores possible), every 0.25 will be a gap
        self.scoreDistributionCounts = [0] * int((3 + 3) / 0.25)
        self.recommendDistributionCounts = [0] * int((1 - 0) / 0.1)

        self.scoreDistributionLabels = [" ~ "] * len(self.scoreDistributionCounts)
        self.recommendDistributionLabels = [" ~ "] * len(self.recommendDistributionCounts)

        for index, col in enumerate(self.scoreDistributionCounts):
            self.scoreDistributionLabels[index] = str(-3 + 0.25 * index) + " ~ " + str(-3 + 0.25 * index + 0.25)

        for index, col in enumerate(self.recommendDistributionCounts):
            self.recommendDistributionLabels[index] = str(0 + 0.1 * index) + " ~ " + str(0 + 0.1 * index + 0.1)

        for submissionID in submissionIDs:
            reviews = [str(line[6]).replace("\r", "") for line in lines if str(line[1]) == submissionID]
            # print reviews
            confidences = [float(review.split("\n")[1].split(": ")[1]) for review in reviews]
            scores = [float(review.split("\n")[0].split(": ")[1]) for review in reviews]

            self.confidenceList.append(sum(confidences) / len(confidences))
            # recommends = [1.0 for review in reviews if review.split("\n")[2].split(": ")[1] == "yes" else 0.0]
            try:
                recommends = map(lambda review: 1.0 if review.split("\n")[2].split(": ")[1] == "yes" else 0.0, reviews)
            except:
                recommends = [0.0 for n in range(len(reviews))]
            weightedScore = sum(x * y for x, y in zip(scores, confidences)) / sum(confidences)
            weightedRecommend = sum(x * y for x, y in zip(recommends, confidences)) / sum(confidences)

            scoreColumn = min(int((weightedScore + 3) / 0.25), 23)
            recommendColumn = min(int((weightedRecommend) / 0.1), 9)
            self.scoreDistributionCounts[scoreColumn] += 1
            self.recommendDistributionCounts[recommendColumn] += 1
            self.submissionIDReviewMap[submissionID] = {'score': weightedScore, 'recommend': weightedRecommend}
            self.scoreList.append(weightedScore)
            self.recommendList.append(weightedRecommend)


    def getReviewInfo(self):
        parsedResult = {}
        parsedResult['IDReviewMap'] = self.submissionIDReviewMap
        parsedResult['scoreList'] = self.scoreList
        parsedResult['meanScore'] = sum(self.scoreList) / len(self.scoreList)
        parsedResult['meanRecommend'] = sum(self.recommendList) / len(self.recommendList)
        parsedResult['meanConfidence'] = sum(self.confidenceList) / len(self.confidenceList)
        parsedResult['recommendList'] = self.recommendList
        parsedResult['scoreDistribution'] = {'labels': self.scoreDistributionLabels, 'counts': self.scoreDistributionCounts}
        parsedResult['recommendDistribution'] = {'labels': self.recommendDistributionLabels,
                                                 'counts': self.recommendDistributionCounts}

        return {'infoType': 'review', 'infoData': parsedResult}
