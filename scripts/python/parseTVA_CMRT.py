# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET


tva_file = sys.argv[1]
outfile_path = sys.argv[2]
country = sys.argv[3]
process_date = sys.argv[4]


def ifnull(var, val):
  if var is None:
    return val
  return var


# check input file
if not os.path.exists(tva_file):
    print 'input file', tva_file, 'does not exist'
    sys.exit(-1)

tree = ET.parse(tva_file)
root = tree.getroot()
rootNS = 'urn:tva:metadata:2010' 
xmlNS = 'http://www.w3.org/XML/1998/namespace'
xsiNS= "http://www.w3.org/2001/XMLSchema-instance"

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
						episodeTitleRow.append(ifnull(episode_number,'').encode('utf8'))
						episodeTitleRow.append(ifnull(series_crid,'').encode('utf8'))
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
						episodeTitleRow.append(ifnull(episode_number,'').encode('utf8'))
						episodeTitleRow.append(ifnull(series_crid,'').encode('utf8'))
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
					title = ifnull(basicDescription.text,'')

					groupTitleRow.append(crid.encode('utf8'))
					groupTitleRow.append(title.encode('utf8'))
					groupTitleRow.append(content_type) # Type of Content
					groupTitleRow.append(ifnull(series_number,'')) # Series Number
					groupTitleRow.append(parent_crid)
					groupTitleRow.append('')
					groupTitleRow.append(language)
					groupTitleRow.append(country)
					groupTitleRow.append(process_date)

					episodeTitlesWriter.writerow(groupTitleRow)
					groupTitleRow = []

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

				genre_type = titles.attrib.get('type')
				genre_classification = titles.attrib.get('href').rsplit(':',1)[0]
				genre_code = titles.attrib.get('href').rsplit(':',1)[-1]

				#genre_language =  titles.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") #Episode Language

				for genre in titles:

					genre = genre.text

					genreRow.append(episode_crid.encode('utf8'))
					genreRow.append('en')
					genreRow.append(genre_type)
					genreRow.append(genre_classification)
					genreRow.append(genre_code)
					genreRow.append(ifnull(genre,'').encode('utf8'))
					genreRow.append(country)
					genreRow.append(process_date)

					genreWriter.writerow(genreRow)
					genreRow = []



subGenreRow = []

search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)   
ProgramInformationTable = tree.getroot().find(search_string)

for ProgramInformation in ProgramInformationTable:

	if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
		episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid

	for basicDescription in ProgramInformation:
		
		for titles in basicDescription:
			if titles.tag == '{urn:tva:metadata:2010}Keyword' and titles.attrib.get('type') == 'other' and titles.text.startswith('Subgenres::'):

				genre = titles.text
				episode_language =  titles.attrib.get("{%s}lang" %xmlNS) #Episode Language

				subGenreRow.append(episode_crid.encode('utf8'))
				subGenreRow.append(episode_language)
				subGenreRow.append('sub')
				subGenreRow.append('')
				subGenreRow.append('')
				subGenreRow.append(genre.encode('utf8'))
				subGenreRow.append(country)
				subGenreRow.append(process_date)

				genreWriter.writerow(subGenreRow)
				subGenreRow = []

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


################################################
#
#	Parsing Credits Data to File
#
################################################
creditsWriter = csv.writer(open(outfile_path + '/CMRT_content_credits_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

#create a list with headings for our columns
headers = 	[ 'crid'
			, 'language'
			, 'given_name'
			, 'family_name'
			, 'presentation_role'
			, 'country'
			, 'process_date'
			]

# Write the row of headings to our CSV file
creditsWriter.writerow(headers)
creditRow = []

presentation_role = ''
given_name = ''
family_name = ''

search_string = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)   
ProgramInformationTable = tree.getroot().find(search_string)

for ProgramInformation in ProgramInformationTable:

	if ProgramInformation.tag == "{%s}ProgramInformation" % (rootNS): 
		episode_crid = ProgramInformation.attrib.get('programId') #Episode Crid

	for basicDescription in ProgramInformation:
		
		for creditList in basicDescription:

			episode_language =  creditList.attrib.get("{%s}lang" %xmlNS) #Episode Language

			if creditList.tag == '{urn:tva:metadata:2010}CreditsList':			
				for creditItem in creditList:

					if creditItem.attrib.get("role").endswith('ACTOR'):

						for credit in creditItem:

							if credit.tag == '{urn:tva:metadata:2010}PersonName':
								
								language = credit.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")

								for person in credit:

									if person.tag == '{urn:tva:mpeg7:2008}FamilyName':
										family_name = person.text
									elif person.tag == '{urn:tva:mpeg7:2008}GivenName':
										given_name = person.text									


							if credit.tag == '{urn:tva:metadata:2010}PresentationRole':
								presentation_role = credit.text
							else:
								presentation_role = ''

						creditRow.append(episode_crid.encode('utf8'))
						creditRow.append(language.encode('utf8'))
						creditRow.append(ifnull(given_name,'').encode('utf8'))
						creditRow.append(ifnull(family_name,'').encode('utf8'))
						creditRow.append(ifnull(presentation_role,'').replace('\n','').replace('\r','').encode('utf8'))
						creditRow.append(country)
						creditRow.append(process_date)
						
						creditsWriter.writerow(creditRow)
						
						creditRow = []		


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
					synopsisRow.append(ifnull(synopsis_type,'').encode('utf8'))
					synopsisRow.append(ifnull(synopsis,'').replace('\n','').replace('\r','').encode('utf8'))
					synopsisRow.append(country)
					synopsisRow.append(process_date)

					synopsisWriter.writerow(synopsisRow)
					synopsisRow = []

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
						
						pg_code = ifnull(pg.attrib.get('href'),'nodata').rsplit(':',1)[0]
						pg_classification = ifnull(pg.attrib.get('href'),'nodata').rsplit(':',1)[-1]

						for name in pg:
							pg_lang = name.attrib.get("{%s}lang" %xmlNS)

					ifnull(pg_lang, ProgramInformation.attrib.get("{%s}lang" %xmlNS))

					pgRow.append(episode_crid.encode('utf8'))
					pgRow.append(pg_code)
					pgRow.append(pg_classification)
					pgRow.append(pg_lang)
					pgRow.append(country)
					pgRow.append(process_date)

					pgWriter.writerow(pgRow)
					pgRow = []

################################################
#
#	Parsing Content Distributer Data to File
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
		lang =  creditList.attrib.get("{%s}lang" %xmlNS) #Episode Language

	for basicDescription in ProgramInformation:
		
		for creditList in basicDescription:

			if ifnull(creditList.attrib.get('href'),'') == 'urn:schange:metadata:cs:CustomTitlePropertyCS:2012:Broadcaster':

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
					content_dist.append(ifnull(studio,'').encode('utf8'))
					content_dist.append(ifnull(broadcaster,'').encode('utf8'))
					content_dist.append(ifnull(channel_name,'').encode('utf8'))
					content_dist.append(creditItem[0].attrib.get("{%s}lang" %xmlNS)) #Episode Language)
					content_dist.append(country)
					content_dist.append(process_date)

					studioWriter.writerow(content_dist)
					content_dist = []

					studio = ''
					channel_name = ''
					broadcaster=''

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
		scheduleRow.append(country)
		scheduleRow.append(process_date)	

		scheduleWriter.writerow(scheduleRow)
		scheduleRow = []
