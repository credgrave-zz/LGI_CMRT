# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteContent(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):

################################################
#
#	Parsing Content Titles to File
#
################################################
	episodeTitlesWriter = csv.writer(open(outfile_path + '/CMRT_content_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

	#create a list with headings for our columns
	headers = 	[ 'crid'
				, 'title'
				, 'type'
				, 'episodeNumber'
				, 'parent_crid'
				, 'hasMemberOf'
				, 'language'
				, 'country'
				, 'process_date'
				]

	# Write the row of headings to our CSV file
	episodeTitlesWriter.writerow(headers)

	search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)        
	ProgramInformationTable = tree.getroot().find(search_string)
	episodeTitleRow = []
	episode_title = ''
	language = ''

	for ProgramInformation in ProgramInformationTable:

		series_crid = ''
		episode_title = ''
		episode_number = ''
		language = ''	
		hasEpisodeTitle = 0	

		if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
			episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid
			
			hasMemberOf = 0

			for basicDescription in ProgramInformation:
					
				if basicDescription.tag == '{urn:tva:metadata:2010}EpisodeOf':
					series_crid = basicDescription.attrib.get('crid') # Series Crid
					episode_number = basicDescription.attrib.get('index') #Episode Number

				if basicDescription.tag == '{urn:tva:metadata:2010}MemberOf':
					hasMemberOf = 1

			for basicDescription in ProgramInformation:
				
					for titles in basicDescription:
						
						# There are some records with No episode titles (e.g. crid://bds.tv/545487377)
						# If the record has an episodeTitle, then we want that. otherwise grab the main Titles
						if titles.tag == '{urn:tva:metadata:2010}Title' and titles.attrib.get('type') == 'episodeTitle':
							hasEpisodeTitle = 1

					for titles in basicDescription:
						
						if hasEpisodeTitle == 1 and titles.tag == '{urn:tva:metadata:2010}Title' and titles.attrib.get('type') == 'episodeTitle':
							
							episode_title = titles.text #Episode Title					
							episode_language =  titles.attrib.get("{%s}lang" %xmlNS) #Episode Language

							episodeTitleRow.append(episode_crid.encode('utf8'))
							episodeTitleRow.append(episode_title.encode('utf8'))
							episodeTitleRow.append('episode') # Type of Content
							episodeTitleRow.append(tvaUtil.ifnull(episode_number,'').encode('utf8'))
							episodeTitleRow.append(tvaUtil.ifnull(series_crid,'').encode('utf8'))
							episodeTitleRow.append(hasMemberOf)
							episodeTitleRow.append(episode_language)
							episodeTitleRow.append(country)
							episodeTitleRow.append(process_date)

							episodeTitlesWriter.writerow(episodeTitleRow)
							episodeTitleRow = []

						elif hasEpisodeTitle == 0 and titles.tag == '{urn:tva:metadata:2010}Title' and (titles.attrib.get('type') == 'main' or titles.attrib.get('type') == None):

							episode_title = titles.text #Episode Title					
							episode_language =  titles.attrib.get("{%s}lang" %xmlNS) #Episode Language

							episodeTitleRow.append(episode_crid.encode('utf8'))
							episodeTitleRow.append(episode_title.encode('utf8'))
							episodeTitleRow.append('episode') # Type of Content
							episodeTitleRow.append(tvaUtil.ifnull(episode_number,'').encode('utf8'))
							episodeTitleRow.append(tvaUtil.ifnull(series_crid,'').encode('utf8'))
							episodeTitleRow.append(hasMemberOf)
							episodeTitleRow.append(episode_language)
							episodeTitleRow.append(country)
							episodeTitleRow.append(process_date)

							episodeTitlesWriter.writerow(episodeTitleRow)
							episodeTitleRow = []


	####################################################################
	#
	# Look in the GroupInformationTable for the Series and Show Details
	#
	####################################################################
	search_string = "{%s}ProgramDescription/{%s}GroupInformationTable" % (rootNS,rootNS)
	groupInformationTable = tree.getroot().find(search_string)

	groupTitleRow = []
	content_type = ''
	title = ''
	parent_crid = ''
	language = ''
	series_number = ''

	for groupInformation in groupInformationTable:
		
		crid = groupInformation.attrib.get('groupId')
		parent_crid = groupInformation[2].attrib.get('crid')
		series_number = groupInformation[2].attrib.get('index')

		for groupType in groupInformation:
			
			if groupType.tag == '{urn:tva:metadata:2010}GroupType':
				content_type = groupType.attrib.get('value')

			elif groupType.tag == '{urn:tva:metadata:2010}BasicDescription':
				
				for basicDescription in groupType:

					if basicDescription.tag == '{urn:tva:metadata:2010}Title':
						
						language = basicDescription.attrib.get("{%s}lang" %xmlNS)
						title = tvaUtil.ifnull(basicDescription.text,'')

						groupTitleRow.append(crid.encode('utf8'))
						groupTitleRow.append(title.encode('utf8'))
						groupTitleRow.append(content_type) # Type of Content
						groupTitleRow.append(tvaUtil.ifnull(series_number,'')) # Series Number
						groupTitleRow.append(parent_crid)
						groupTitleRow.append('')
						groupTitleRow.append(language)
						groupTitleRow.append(country)
						groupTitleRow.append(process_date)

						episodeTitlesWriter.writerow(groupTitleRow)
						groupTitleRow = []
