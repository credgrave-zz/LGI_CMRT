# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteContentKeywords(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):
	
################################################
#
#	Parsing Keyword Data to File
#
################################################
	keywordWriter = csv.writer(open(outfile_path + '/CMRT_content_keywords_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

	#create a list with headings for our columns
	headers = 	[ 'crid'
				, 'language'
				, 'keyword'
				, 'country'
				, 'process_date'
				]

	# Write the row of headings to our CSV file
	keywordWriter.writerow(headers)
	keywordRow = []
	search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)   
	ProgramInformationTable = tree.getroot().find(search_string)

	for ProgramInformation in ProgramInformationTable:

		if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
			episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid

		for basicDescription in ProgramInformation:
			
			for titles in basicDescription:
				if titles.tag == '{urn:tva:metadata:2010}Keyword':

					keyword = titles.text
					episode_language =  titles.attrib.get("{%s}lang" %xmlNS) #Episode Language

					keywordRow.append(episode_crid.encode('utf8'))
					keywordRow.append(episode_language)
					keywordRow.append(keyword.encode('utf8'))
					keywordRow.append(country)
					keywordRow.append(process_date)

					keywordWriter.writerow(keywordRow)
					keywordRow = []		

