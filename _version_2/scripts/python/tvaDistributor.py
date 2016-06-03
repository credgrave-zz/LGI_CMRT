# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteContentDistributor(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):
	
################################################
#
#	Parsing Content Distributor Data to File
#
################################################
	studioWriter = csv.writer(open(outfile_path + '/CMRT_content_distributor_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

	#create a list with headings for our columns
	headers = 	[ 'crid'
				, 'studio'
				, 'broadcaster'
				, 'channel_name'
				, 'lang'
				, 'country'
				, 'process_date'
				]

	# Write the row of headings to our CSV file
	studioWriter.writerow(headers)

	search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)   
	ProgramInformationTable = tree.getroot().find(search_string)

	content_dist = []
	studio = ''
	channel_name = ''
	broadcaster=''

	for ProgramInformation in ProgramInformationTable:

		if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
			episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid

		for basicDescription in ProgramInformation:
			
			for creditList in basicDescription:

				if tvaUtil.ifnull(creditList.attrib.get('href'),'') == 'urn:schange:metadata:cs:CustomTitlePropertyCS:2012:Broadcaster':

					broadcaster = creditList[0].text 

				if creditList.tag == '{urn:tva:metadata:2010}CreditsList':			
					for creditItem in creditList:

						if creditItem.attrib.get("role").endswith('STUDIO'): 

							studio = creditItem[0].text

						elif creditItem.attrib.get("role") == 'urn:eventis:metadata:cs:RoleCS:2010:CONTENT-PROVIDER':

							channel_name = creditItem[0].text

					if channel_name == '' and studio == '' and broadcaster == '':

						None

					else:

						content_dist.append(episode_crid.encode('utf8'))
						content_dist.append(tvaUtil.ifnull(studio,'').encode('utf8'))
						content_dist.append(tvaUtil.ifnull(broadcaster,'').encode('utf8'))
						content_dist.append(tvaUtil.ifnull(channel_name,'').encode('utf8'))
						content_dist.append(creditItem[0].attrib.get("{%s}lang" %xmlNS)) #Episode Language)
						content_dist.append(country)
						content_dist.append(process_date)

						studioWriter.writerow(content_dist)
						content_dist = []

						studio = ''
						channel_name = ''
						broadcaster=''