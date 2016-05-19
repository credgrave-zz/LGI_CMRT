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
				, 'ditto_country'
				, 'ditto_date'
				]

	# Write the row of headings to our CSV file
	writer.writerow(headers)

	with open(infile_json,'r') as json_file:
		json_data=json_file.read()


	json_file=json.loads(json_data)


	 check input file
	if not os.path.exists(infile_json):
	    print 'input file', infile_json, 'does not exist'
	    sys.exit(-1)

	# Loop through the TVA_OnDemandProgramTable Entity and Grab 
	# the data we need and add it to the csv file as a single row per system
	for record in json_file[u'TVA_OnDemandProgramTable']:
		
		try:
			# Add MSS Attributes
			MSS_csv_row = []

			MSS_csv_row.append('MSS')
			MSS_csv_row.append(record[u'OnDemandProgram'][u'Program'][u'crid'])
			MSS_csv_row.append(record[u'_MSS'][u'request'])
			MSS_csv_row.append(record[u'_MSS'][u'available'][u'requestTime'])
			MSS_csv_row.append('')
			MSS_csv_row.append(record[u'_MSS'][u'available'][u'exists'])
			MSS_csv_row.append(record[u'_MSS'][u'AvailabilityTime'])
			MSS_csv_row.append('')
			MSS_csv_row.append(ditto_country)
			MSS_csv_row.append(ditto_date)

			writer.writerow(MSS_csv_row)
			MSS_csv_row = []

			# Add TRAXIS Attributes

			TRAXIS_csv_row = []

			TRAXIS_csv_row.append('TRAXIS')
			TRAXIS_csv_row.append(record[u'OnDemandProgram'][u'Program'][u'crid'])
			TRAXIS_csv_row.append(record[u'_TRAXIS'][u'request'])
			TRAXIS_csv_row.append(record[u'_TRAXIS'][u'available'][u'requestTime'])
			TRAXIS_csv_row.append('')
			TRAXIS_csv_row.append(record[u'_TRAXIS'][u'available'][u'exists'])
			TRAXIS_csv_row.append(record[u'_TRAXIS'][u'AvailabilityTime'])
			TRAXIS_csv_row.append('')
			TRAXIS_csv_row.append(ditto_country)
			TRAXIS_csv_row.append(ditto_date)

			writer.writerow(TRAXIS_csv_row)
			TRAXIS_csv_row = []

			# Add CMDC Attributes

			CDMC_csv_row = []

			CDMC_csv_row.append('CMDC')
			CDMC_csv_row.append(record[u'OnDemandProgram'][u'Program'][u'crid'])
			CDMC_csv_row.append(record[u'_CMDC'][u'request'])
			CDMC_csv_row.append(record[u'_CMDC'][u'available'][u'requestTime'])
			CDMC_csv_row.append('')
			CDMC_csv_row.append(record[u'_CMDC'][u'available'][u'exists'])
			CDMC_csv_row.append(record[u'_CMDC'][u'AvailabilityTime'])
			CDMC_csv_row.append('')
			CDMC_csv_row.append(ditto_country)
			CDMC_csv_row.append(ditto_date)

			writer.writerow(CDMC_csv_row)	
			CDMC_csv_row = []

			# Add RENG Attributes

			RENG_csv_row = []

			RENG_csv_row.append('RENG')
			RENG_csv_row.append(record[u'OnDemandProgram'][u'Program'][u'crid'])
			RENG_csv_row.append(record[u'_RENG'][u'request'])
			RENG_csv_row.append(record[u'_RENG'][u'available'][u'requestTime'])
			RENG_csv_row.append('')
			RENG_csv_row.append(record[u'_RENG'][u'available'][u'exists'])
			RENG_csv_row.append(record[u'_RENG'][u'AvailabilityTime'])
			RENG_csv_row.append('')
			RENG_csv_row.append(ditto_country)
			RENG_csv_row.append(ditto_date)

			writer.writerow(RENG_csv_row)
			RENG_csv_row = []
			
			# Add SMARTREC Attributes

			SMARTREC_csv_row = []

			SMARTREC_csv_row.append('SMARTREC')
			SMARTREC_csv_row.append(record[u'OnDemandProgram'][u'Program'][u'crid'])
			SMARTREC_csv_row.append(record[u'_SMARTREC'][u'request'])
			SMARTREC_csv_row.append(record[u'_SMARTREC'][u'available'][u'requestTime'])
			SMARTREC_csv_row.append(record[u'_SMARTREC'][u'available'][u'exist'])
			SMARTREC_csv_row.append(record[u'_SMARTREC'][u'available'][u'exists'])
			SMARTREC_csv_row.append(record[u'_SMARTREC'][u'AvailabilityTime'])
			SMARTREC_csv_row.append(record[u'_SMARTREC'][u'available'][u'state'])
			SMARTREC_csv_row.append(ditto_country)
			SMARTREC_csv_row.append(ditto_date)

			writer.writerow(SMARTREC_csv_row)
			SMARTREC_csv_row = []

		except:
			pass
