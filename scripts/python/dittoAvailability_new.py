import os
import json
import csv
import time
import sys

###################################################################
# __author__ "Chris Redgrave"
# __version__ "001"
# __status__ "Development"
#
# Description:
# This script will process a json file provided from the
# Ditto team into a TSV (Tab-Seperated) File
#
# Version 	Author 		Date 		Description
###################################################################
# 001		C.Redgrave	16/01/2016	Original Version
# 002		C.Redgrave	27/01/2016	Included exception handling
#									for missing systems
###################################################################
def parseWriteDittoAvailability(infile_json, outfile_path, ditto_country, ditto_date):

	writer = csv.writer(open(outfile_path + '/CMRT_ditto_content_availability_' + ditto_country + '_' + ditto_date + '.csv', 'w'), delimiter='|')
	 
	#create a list with headings for our columns
	headers = 	[ 'systemName'
				, 'crid'
				, 'request'
				, 'requestTime'
				, 'exist'
				, 'exists_'
				, 'AvailabilityTime'
				, 'state'
				, 'linearvod'
				, 'ditto_country'
				, 'ditto_date'
				]

	# Write the row of headings to our CSV file
	writer.writerow(headers)

	with open(infile_json,'r') as json_file:
		json_data=json_file.read()


	json_file=json.loads(json_data)
	returnedAvailabilityArray = []

	getAvailabilityArray(json_file, 'TVA_OnDemandProgramTable', returnedAvailabilityArray, 'vod', ditto_country, ditto_date)
	getAvailabilityArray(json_file, 'TVA_ScheduleEventTable', returnedAvailabilityArray, 'linear', ditto_country, ditto_date)
	
	for record in returnedAvailabilityArray:

		writer.writerow(record)


def getAvailabilityArray(jsonFile, baseJsonTree, returnedAvailabilityArray, vodlinear, inDittoCountry, inDittoDate):	
	
	for record in jsonFile[baseJsonTree]:

		recordName = baseJsonTree.replace('Table','').replace('TVA_','')
		availabilityRecordArray = []

		try:				
			recordCrid = record[recordName][u'Program'][u'crid']
		except KeyError:
			availabilityRecordArray.append('no crid') 	

		for content in record:

			if content not in ('_id', '_created', '_updated', recordName):
				
				availabilityRecordArray = []
				
				try:					
					availabilityRecordArray.append(content) # System Name	
				except KeyError:
					availabilityRecordArray.append('') 	

				try:
					
					availabilityRecordArray.append(recordCrid)
				except KeyError:
					availabilityRecordArray.append('') 	

				try:
					availabilityRecordArray.append(record[content][u'request'])
				except KeyError:
					availabilityRecordArray.append('') 	

				try:
					availabilityRecordArray.append(record[content][u'available'][u'requestTime'])
				except KeyError:
					availabilityRecordArray.append('') 	

				try:
					availabilityRecordArray.append(record[content][u'available'][u'exist'])

				except KeyError:
					availabilityRecordArray.append('') 	

				try:
					availabilityRecordArray.append(record[content][u'available'][u'exists'])

				except KeyError:
					availabilityRecordArray.append('') 	

				try:
					availabilityRecordArray.append(record[content][u'AvailabilityTime'])

				except KeyError:
					availabilityRecordArray.append('') 						

				try:
					availabilityRecordArray.append(record[content][u'available'][u'state'])

				except KeyError:
					availabilityRecordArray.append('') 						
				
				availabilityRecordArray.append(vodlinear)
				availabilityRecordArray.append(inDittoCountry)
				availabilityRecordArray.append(inDittoDate)

				returnedAvailabilityArray.append(availabilityRecordArray)

