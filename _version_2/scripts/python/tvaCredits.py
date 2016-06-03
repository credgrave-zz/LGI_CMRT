# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteContentCredits(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):

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
							creditRow.append(tvaUtil.ifnull(given_name,'').encode('utf8'))
							creditRow.append(tvaUtil.ifnull(family_name,'').encode('utf8'))
							creditRow.append(tvaUtil.ifnull(presentation_role,'').replace('\n','').replace('\r','').encode('utf8'))
							creditRow.append(country)
							creditRow.append(process_date)
							
							creditsWriter.writerow(creditRow)
							
							creditRow = []		
