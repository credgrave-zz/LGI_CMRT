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

	for record in json_file[u'TVA_ScheduleEventTable']:
		
		try:
			# Add MSS Attributes
			#MSS_csv_row = []

			#MSS_csv_row.append('MSS')
			#MSS_csv_row.append(record[u'ScheduleEvent'][u'Program'][u'crid'])
			#MSS_csv_row.append(record[u'_MSS'][u'request'])
			#MSS_csv_row.append(record[u'_MSS'][u'available'][u'requestTime'])
			#MSS_csv_row.append('')
			#MSS_csv_row.append(record[u'_MSS'][u'available'][u'exists'])
			#MSS_csv_row.append(record[u'_MSS'][u'AvailabilityTime'])
			#MSS_csv_row.append('')
			#MSS_csv_row.append('linear')
			#MSS_csv_row.append(ditto_country)
			#MSS_csv_row.append(ditto_date)

			#writer.writerow(MSS_csv_row)
			#MSS_csv_row = []

			# Add CMDC Attributes

			CMDC_csv_row = []

			CMDC_csv_row.append('CDMC')
			CMDC_csv_row.append(record[u'ScheduleEvent'][u'Program'][u'crid'])
			CMDC_csv_row.append(record[u'_CDMC'][u'request'])
			CMDC_csv_row.append(record[u'_CDMC'][u'available'][u'requestTime'])
			CMDC_csv_row.append('')
			CMDC_csv_row.append('')
			CMDC_csv_row.append(record[u'_CDMC'][u'AvailabilityTime'])
			CMDC_csv_row.append('')
			CMDC_csv_row.append('linear')
			CMDC_csv_row.append(ditto_country)
			CMDC_csv_row.append(ditto_date)

			writer.writerow(CMDC_csv_row)
			CMDC_csv_row = []

  		

		except:
			raise