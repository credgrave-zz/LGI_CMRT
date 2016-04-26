# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteParentalGuidance(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):
	
################################################
#
#	Parsing Parental Guidance Data to File
#
################################################
	pgWriter = csv.writer(open(outfile_path + '/CMRT_content_certification_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

	#create a list with headings for our columns
	headers = 	[ 'crid'
				, 'classification'
				, 'id'
				, 'lang'
				, 'country'
				, 'process_date'
				]

	# Write the row of headings to our CSV file
	pgWriter.writerow(headers)
	pgRow = []
	pg_lang = ''

	search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)   
	ProgramInformationTable = tree.getroot().find(search_string)

	for ProgramInformation in ProgramInformationTable:

		if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
			episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid

		for basicDescription in ProgramInformation:
					
			for titles in basicDescription:
					
				if titles.tag == '{urn:tva:metadata:2010}ParentalGuidance':

					for pg in titles:

						if pg.tag == '{urn:tva:mpeg7:2008}MinimumAge':
							
							pg_code = pg.text
							pg_classification = 'MinimumAge'
							pg_lang = ProgramInformation.attrib.get("{%s}lang" %xmlNS)
						
						elif pg.tag == '{urn:tva:mpeg7:2008}ParentalRating':
							
							pg_code = tvaUtil.ifnull(pg.attrib.get('href'),'nodata').rsplit(':',1)[0]
							pg_classification = tvaUtil.ifnull(pg.attrib.get('href'),'nodata').rsplit(':',1)[-1]

							for name in pg:
								pg_lang = name.attrib.get("{%s}lang" %xmlNS)

						tvaUtil.ifnull(pg_lang, ProgramInformation.attrib.get("{%s}lang" %xmlNS))

						pgRow.append(episode_crid.encode('utf8'))
						pgRow.append(pg_code)
						pgRow.append(pg_classification)
						pgRow.append(pg_lang)
						pgRow.append(country)
						pgRow.append(process_date)

						pgWriter.writerow(pgRow)
						pgRow = []