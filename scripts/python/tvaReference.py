# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteReferenceData(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):
################################################
#
#	Parsing Reference Data to File
#
################################################
	referenceWriter = csv.writer(open(outfile_path + '/CMRT_reference_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

	#create a list with headings for our columns
	headers = 	[ 'classification'
				, 'language'
				, 'key'
				, 'value'
				, 'country'
				, 'process_date'
				]

	# Write the row of headings to our CSV file
	referenceWriter.writerow(headers)


	search_string = "{%s}ClassificationSchemeTable" % (rootNS)        
	classificationSchemeTable = tree.getroot().find(search_string)

	for classificationSchemes in classificationSchemeTable:
		
		language = classificationSchemes.attrib.get("{%s}lang" %xmlNS )
		classificationName = classificationSchemes.attrib.get('uri')
		referenceDataRow = []

		if classificationName == 'urn:eventis:metadata:cs:AgeCS:2010':
			
			for classification in classificationSchemes:
				key = classification.attrib.get('termID')
				
				for terms in classification:
					referenceDataRow.append(classificationName) #Classification
					referenceDataRow.append(language) #language
					referenceDataRow.append(key) #Key
					referenceDataRow.append(terms.text) #Value
					referenceDataRow.append(country)
					referenceDataRow.append(process_date)	
					
					referenceWriter.writerow(referenceDataRow)
					referenceDataRow = []

		elif classificationName == 'urn:tva:metadata:cs:UPCAgeRatingCS:2008':

			for classification in classificationSchemes:
				key = classification.attrib.get('termID')
				
				for terms in classification:
					referenceDataRow.append(classificationName) #Classification
					referenceDataRow.append(terms.attrib.get("{%s}lang" %xmlNS )) #language
					referenceDataRow.append(key) #Key
					referenceDataRow.append(terms.text) #Value
					referenceDataRow.append(country)
					referenceDataRow.append(process_date)	
					
					referenceWriter.writerow(referenceDataRow)
					referenceDataRow = []

		elif classificationName == 'urn:tva:metadata:cs:UPCEventGenreCS:2009':

			for classification in classificationSchemes:
				key = classification.attrib.get('termID')
				
				for terms in classification:
					referenceDataRow.append(classificationName) #Classification
					referenceDataRow.append(terms.attrib.get("{%s}lang" %xmlNS )) #language				
					referenceDataRow.append(key) #Key
					referenceDataRow.append(tvaUtil.ifnull(terms.text,'').encode('utf8')) #Value
					referenceDataRow.append(country)
					referenceDataRow.append(process_date)	
					
					referenceWriter.writerow(referenceDataRow)
					referenceDataRow = []
