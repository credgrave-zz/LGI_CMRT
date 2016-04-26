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
#	Parsing Genre Data to File
#
################################################
genreWriter = csv.writer(open(outfile_path + '/CMRT_content_genre_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

#create a list with headings for our columns
headers = 	[ 'crid'
			, 'language'
			, 'genre_type'
			, 'genre_classification'
			, 'genre_code'
			, 'genre_value'
			, 'country'
			, 'process_date'
			]

# Write the row of headings to our CSV file
genreWriter.writerow(headers)
genreRow = []

genre_language = ''

search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)   
ProgramInformationTable = tree.getroot().find(search_string)

for ProgramInformation in ProgramInformationTable:

	if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
		episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid

	for basicDescription in ProgramInformation:
				
		for titles in basicDescription:
				
			if titles.tag == '{urn:tva:metadata:2010}Genre' and titles.attrib.get('type') == 'main':

				genre_language = ''
				genre_type = titles.attrib.get('type')
				genre_classification = titles.attrib.get('href').rsplit(':',1)[0]
				genre_code = titles.attrib.get('href').rsplit(':',1)[-1]

				for genre in titles:

					genre_language =  genre.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") #Episode Language

					genre = genre.text

					genreRow.append(episode_crid.encode('utf8'))
					genreRow.append(genre_language)
					genreRow.append(genre_type)
					genreRow.append(genre_classification)
					genreRow.append(genre_code)
					genreRow.append(ifnull(genre,'').encode('utf8'))
					genreRow.append(country)
					genreRow.append(process_date)

					genreWriter.writerow(genreRow)
					genreRow = []




