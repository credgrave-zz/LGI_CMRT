# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

def ifnull(var, val):
  if var is None:
    return val
  return var

tva_file = sys.argv[1]
outfile_path = sys.argv[2]
country = sys.argv[3]
process_date = sys.argv[4]

tree = ET.parse(tva_file)
root = tree.getroot()
rootNS = 'urn:tva:metadata:2010' 
xmlNS = 'http://www.w3.org/XML/1998/namespace'
xsiNS= "http://www.w3.org/2001/XMLSchema-instance"

################################################
#
#	Parsing Schedule Data to File
#
################################################
scheduleWriter = csv.writer(open(outfile_path + '/CMRT_content_schedule_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

#create a list with headings for our columns
headers = 	[ 'crid'
			, 'startTime'
			, 'endTime'
			, 'channel_name'
			, 'country'
			, 'process_date'
			]

# Write the row of headings to our CSV file
scheduleWriter.writerow(headers)
scheduleRow = []
search_string = "{%s}ProgramDescription/{%s}ProgramLocationTable" % (rootNS,rootNS)   
ProgramScheduleTable = tree.getroot().find(search_string)

for ProgramSchedule in ProgramScheduleTable:
	
	if ProgramSchedule.tag == '{urn:tva:metadata:2010}BroadcastEvent':
		scheduleCrid = ''
		scheduleStartTime = ''
		scheduleEndTime = ''
		channel_name = ''
		
		print ProgramSchedule.attrib
		channel_name = ProgramSchedule.attrib.get("serviceIDRef")
		
		for scheduleAttributes in ProgramSchedule:
	

			if scheduleAttributes.tag == '{urn:tva:metadata:2010}Program':
				
				scheduleCrid = scheduleAttributes.attrib.get("crid")

			if scheduleAttributes.tag == '{urn:tva:metadata:2010}PublishedStartTime':
				
				scheduleStartTime = scheduleAttributes.text

			if scheduleAttributes.tag == '{urn:tva:metadata:2010}PublishedEndTime':
				
				scheduleEndTime = scheduleAttributes.text

		scheduleRow.append(scheduleCrid)
		scheduleRow.append(ifnull(scheduleStartTime,''))	
		scheduleRow.append(ifnull(scheduleEndTime,''))
		scheduleRow.append(ifnull(channel_name,''))
		scheduleRow.append(country)
		scheduleRow.append(process_date)	

		scheduleWriter.writerow(scheduleRow)
		scheduleRow = []





