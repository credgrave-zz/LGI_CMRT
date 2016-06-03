# This Python file uses the following encoding: utf-8
import os
import sys
import re
import csv
import xml.etree.cElementTree as ET

import tvaUtil

def parseWriteContentOnDemand(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path):

################################################
#
#   Parsing On Demand List Data to File
#
################################################
    onDemandWriter = csv.writer(open(outfile_path + '/CMRT_content_onDemand_' + country + '_' + process_date + '.csv', 'w'),delimiter='|')

    #create a list with headings for our columns
    headers =   [ 'crid'
                , 'country'
                , 'process_date'
                ]

    # Write the row of headings to our CSV file
    onDemandWriter.writerow(headers)
    onDemandRow = []
    search_string = "{%s}ProgramDescription/{%s}ProgramLocationTable" % (rootNS,rootNS)   
    ProgramOnDemandTable = tree.getroot().find(search_string)

    for ProgramOnDemand in ProgramOnDemandTable:
        
        if ProgramOnDemand.tag == '{urn:tva:metadata:2010}OnDemandProgram':

            scheduleCrid = ''
            
            for onDemandAttributes in ProgramOnDemand:      

                if onDemandAttributes.tag == '{urn:tva:metadata:2010}Program':
                    
                    onDemandCrid = onDemandAttributes.attrib.get("crid")

            onDemandRow.append(onDemandCrid)
            onDemandRow.append(country)
            onDemandRow.append(process_date)    

            onDemandWriter.writerow(onDemandRow)
            onDemandRow = []

