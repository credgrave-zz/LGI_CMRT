# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteContentSynopsis(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):
	
################################################
#
#	Parsing Synopsis Data to File
#
################################################
	#synopsisWriter = csv.writer(open(outfile_path + '/CMRT_content_synopsis_' + country + '_' + process_date + '.csv', 'w'),delimiter='|', lineterminator='\f')
	synopsisWriter = csv.writer(open(outfile_path + '/CMRT_content_synopsis_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')
	#create a list with headings for our columns
	headers = 	[ 'crid'
				, 'language'
				, 'synopsis_type'
				, 'synopsis'
				, 'country'
				, 'process_date'
				]

	# Write the row of headings to our CSV file
	synopsisWriter.writerow(headers)
	synopsisRow = []	

	synopsis = ''
	synopsis_type = ''
	synop_language = ''
	
	search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)   
	ProgramInformationTable = tree.getroot().find(search_string)

	for ProgramInformation in ProgramInformationTable:
			
		if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
			episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid
		
			for basicDescription in ProgramInformation:
			
				for synop in basicDescription:

					if synop.tag == '{urn:tva:metadata:2010}Synopsis':
						
						synop_language = synop.attrib.get("{%s}lang" %xmlNS)
						synopsis_type = synop.attrib.get('length')
						synopsis = synop.text
						
						synopsisRow.append(episode_crid.encode('utf8'))
						synopsisRow.append(synop_language)
						synopsisRow.append(tvaUtil.ifnull(synopsis_type,'').encode('utf8'))
						synopsisRow.append(tvaUtil.ifnull(synopsis,'').replace('\n','').replace('\r','').encode('utf8'))
						synopsisRow.append(country)
						synopsisRow.append(process_date)

						synopsisWriter.writerow(synopsisRow)
						synopsisRow = []