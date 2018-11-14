# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

import json

from utils import parseCSVFileFromDjangoFile, isNumber, returnTestChartData
from getInsight import parseAuthorCSVFile, getReviewScoreInfo, getAuthorInfo, getReviewInfo, getSubmissionInfo,\
	getAuthorAndSubmissionInfo, getAuthorAndReviewInfo, invalidFiles

# Create your views here.
# Note: a view is a func taking the HTTP request and returns sth accordingly

def index(request):
	return HttpResponse("Hello, world. You're at the polls index.")

def test(request):
	return HttpResponse("<h1>This is the very first HTTP request!</h1>")

# Note: csr: cross site request, adding this to enable request from localhost
@csrf_exempt
def uploadCSV(request):
	print("Inside the upload function")
	if request.FILES:
		# print("Check : ", request.FILES.getlist('file'))
		# csvFile = request.FILES['file']
		# print("checkrequest : ", csvFiles)
		listOfFiles = request.FILES.getlist('file')
		print("How many files : ", len(listOfFiles))
		rowContent = ""
		#Handles single file upload
		if len(listOfFiles) == 1:
			print "Inside single File"
			csvFile = listOfFiles[0]
			fileName = str(csvFile.name)
			print("check file name : ", fileName)
			print("CheckCSVFile : ", type(csvFile))
			if "author.csv" in fileName:
				rowContent = getAuthorInfo(csvFile)
			elif "score.csv" in fileName:
				rowContent = getReviewScoreInfo(csvFile)
			elif "review.csv" in fileName:
				rowContent = getReviewInfo(csvFile)
			elif "submission.csv" in fileName:
				rowContent = getSubmissionInfo(csvFile)
			else:
				#rowContent = returnTestChartData(csvFile)  # return null?
				rowContent = invalidFiles()
		else: # Multi file upload
			fileNameList = []
			for csvFile in listOfFiles:
				fileNameList.append(str(csvFile.name))
			if len(listOfFiles) == 2 and "author.csv" in fileNameList and "submission.csv" in fileNameList:
				rowContent = getAuthorAndSubmissionInfo(listOfFiles)
			elif len(listOfFiles) == 2 and "author.csv" in fileNameList and "review.csv" in fileNameList:
				rowContent = getAuthorAndReviewInfo(listOfFiles)
			else:
				rowContent = invalidFiles()
			# print(type(csvFile.name))

		if request.POST:
	# current problem: request from axios not recognized as POST
			# csvFile = request.FILES['file']
			print("Now we got the csv file")
		print("returnedRow: ", rowContent)
		return HttpResponse(json.dumps(rowContent))
		# return HttpResponse("Got the CSV file.")
	else:
		print("Not found the file!")
		return HttpResponseNotFound('Page not found for CSV')

# Combines 2 dict while keeping both values for same key
def merge_two_dicts(x, y):
	if not y == "":
		result = {}
		for key in (x.viewkeys() | y.keys()):
			if key in x: result.setdefault(key, []).append(x[key])
			if key in y: result.setdefault(key, []).append(y[key])
	else:
		result = x
	return result