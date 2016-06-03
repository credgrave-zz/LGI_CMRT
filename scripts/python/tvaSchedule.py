# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

################################################
#
#	Parsing Schedule Data to File
#
################################################

def parseWriteContentSchedule(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):
	
	scheduleWriter = csv.writer(open(outfile_path + '/CMRT_content_schedule_' + country + '_' + process_date + '.csv', 'w'), delimiter='|')
	
	#create a list with headings for our columns
	headers = [       'crid'
			, 'startTime'
			, 'endTime'
			, 'channel_name'
			, 'country'
			, 'process_date'
			]

	# Write the row of headings to our CSV file
	scheduleWriter.writerow(headers)
	scheduleRow = []
	# program location table contains schedule events get program 
	search_string = "{%s}ProgramDescription/{%s}ProgramLocationTable" % (rootNS,rootNS)
	ProgramScheduleTable = tree.getroot().find(search_string)
	
	for channelSchedule in ProgramScheduleTable:
		if channelSchedule.tag == '{urn:tva:metadata:2010}Schedule':
			channel_name = ''
			channel_name = channelSchedule.attrib.get("serviceIDRef")
			for scheduleEvents in channelSchedule:
				if scheduleEvents.tag == '{urn:tva:metadata:2010}ScheduleEvent':
					scheduleCrid = ''
					scheduleStartTime = ''
					scheduleEndTime = ''
					for scheduleAttributes in scheduleEvents:
						if scheduleAttributes.tag == '{urn:tva:metadata:2010}Program':
							scheduleCrid = scheduleAttributes.attrib.get("crid")
						if scheduleAttributes.tag == '{urn:tva:metadata:2010}PublishedStartTime':
							scheduleStartTime = scheduleAttributes.text
						if scheduleAttributes.tag == '{urn:tva:metadata:2010}PublishedEndTime':
							scheduleEndTime = scheduleAttributes.text
							
					scheduleRow = []
					scheduleRow.append(scheduleCrid)
					scheduleRow.append(tvaUtil.ifnull(scheduleStartTime,''))	
					scheduleRow.append(tvaUtil.ifnull(scheduleEndTime,''))
					scheduleRow.append(tvaUtil.ifnull(channel_name,''))
					scheduleRow.append(country)
					scheduleRow.append(process_date)	
					scheduleWriter.writerow(scheduleRow)


#		if ProgramSchedule.tag == '{urn:tva:metadata:2010}BroadcastEvent':
#			scheduleCrid = ''
#			scheduleStartTime = ''
#			scheduleEndTime = ''
#			channel_name = ''
#			
#			channel_name = ProgramSchedule.attrib.get("serviceIDRef")
#			
#			for scheduleAttributes in ProgramSchedule:
#		
#
#				if scheduleAttributes.tag == '{urn:tva:metadata:2010}Program':
#					
#					scheduleCrid = scheduleAttributes.attrib.get("crid")
#
#				if scheduleAttributes.tag == '{urn:tva:metadata:2010}PublishedStartTime':
#					
#					scheduleStartTime = scheduleAttributes.text
#
#				if scheduleAttributes.tag == '{urn:tva:metadata:2010}PublishedEndTime':
#					
#					scheduleEndTime = scheduleAttributes.text
#
#			scheduleRow.append(scheduleCrid)
#			scheduleRow.append(tvaUtil.ifnull(scheduleStartTime,''))	
#			scheduleRow.append(tvaUtil.ifnull(scheduleEndTime,''))
#			scheduleRow.append(tvaUtil.ifnull(channel_name,''))
#			scheduleRow.append(country)
#			scheduleRow.append(process_date)	
#
#			scheduleWriter.writerow(scheduleRow)
#			scheduleRow = []
#
