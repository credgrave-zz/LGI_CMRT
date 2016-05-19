# This Python file uses the following encoding: utf-8

# Standard Module Imports
import os
import sys
import re
import xml.etree.cElementTree as ET

# Custom Module Imports
import tvaReference
import tvaContent
import tvaGenre
import tvaKeyword
import tvaCredits
import tvaSynopsis
import tvaParentalGuidance
import tvaDistributor
import tvaSchedule
import tvaOnDemand

#Arguments
tva_file = sys.argv[1]
outfile_path = sys.argv[2]
country = sys.argv[3]
process_date = sys.argv[4]

# check input file
#if not os.path.exists(tva_file):
#    print 'input file', tva_file, 'does not exist'
#    sys.exit(-1)

# XML Constants
tree = ET.parse(tva_file)
root = tree.getroot()
rootNS = 'urn:tva:metadata:2010' 
xmlNS = 'http://www.w3.org/XML/1998/namespace'
xsiNS= "http://www.w3.org/2001/XMLSchema-instance"

#tvaReference.parseWriteReferenceData(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaContent.parseWriteContent(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaGenre.parseWriteContentGenre(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaKeyword.parseWriteContentKeywords(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaCredits.parseWriteContentCredits(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaSynopsis.parseWriteContentSynopsis(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaParentalGuidance.parseWriteParentalGuidance(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaDistributor.parseWriteContentDistributor(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

#tvaSchedule.parseWriteContentSchedule(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)

tvaOnDemand.parseWriteContentOnDemand(process_date, country, tree, rootNS, xmlNS, xsiNS, outfile_path)
