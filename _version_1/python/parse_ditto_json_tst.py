import os, json, csv, time, sys

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


#outfile_path='/home/cloudera/_work/_LGI/file_output/CSV_JSON_OUTPUT.tsv'
#infile_json='/home/cloudera/_work/_LGI/json_input/NL_ditto.json'
#ditto_country='NL' 


infile_json= sys.argv[1]
outfile_path= sys.argv[2]
ditto_country= sys.argv[3]
ditto_date= sys.argv[4]

writer = csv.writer(open(outfile_path + '/' + ditto_country + '_ditto_' + ditto_date + '.tsv', 'w'),delimiter='\t')
 
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

# Loop through the TVA_OnDemandProgramTable Entity and Grab 
# the data we need and add it to the csv file as a single row per system
for record in json_file[u'TVA_OnDemandProgramTable']:
	

	# Add MSS Attributes
	MSS_csv_row = []

	MSS_csv_row.append('MSS')
	MSS_csv_row.append(record[u'OnDemandProgram'][u'Program'][u'crid'])
	MSS_csv_row.append(record[u'_MSS'][u'request'])
	MSS_csv_row.append(record[u'_MSS'][u'available'][u'requestTime'])
	MSS_csv_row.append('NULL')
	MSS_csv_row.append(record[u'_MSS'][u'available'][u'exists'])
	MSS_csv_row.append(record[u'_MSS'][u'AvailabilityTime'])
	MSS_csv_row.append('NULL')
	MSS_csv_row.append(ditto_country)
	MSS_csv_row.append(ditto_date)

	writer.writerow(MSS_csv_row)
