from parseTVA_common import writeTitle

import os
import xml.etree.cElementTree as ET
import csv
import datetime
import calendar
import time
import re
import sys
import codecs
from collections import namedtuple
from collections import defaultdict
"""
    processProgramInformation - create a dictionary of program details
    takes a programInformation element
    adds a ContentDetails tuple to parsedPrograms
    records the referenced SeriesCrid if any in referencedSeriesCrids
    records the ContentProvider info if any in programCrid2ContentProviderMap
    writes out any titles to titleWriter
"""
def processProgramInformation(pi, referencedSeriesCrids, programCrid2ContentProviderMap, parsedPrograms, rootNS, ContentDetails, xmlNS, TitleDetails, allWrittenTitles, titleTuple, titleWriter):

    mainGenre = '00'
    crid = pi.attrib.get('programId')
    basicDesc = pi.find(  "{%s}BasicDescription" % rootNS  )

    Episode = pi.find("{%s}EpisodeOf" % rootNS)
    if Episode != None:
        EpisodeOf = Episode.attrib.get("crid")
        referencedSeriesCrids.add(EpisodeOf)
    else:
        EpisodeOf = ""

            

    CONTENT_PROVIDER=""
    CONTENT_PROVIDER_ID=""
    HasPreview=""
    IsPreviewOf=""

    mainGenreList = []
    for child in basicDesc:
        if child.tag.endswith('CreditsList'):
            # process credits list for CONTENT-PROVIDER and CONTENT-PROVIDER-ID
            for CreditsItem in child:
                if "role" in CreditsItem.attrib and  CreditsItem.attrib["role"].endswith('CONTENT-PROVIDER'):
                    if CONTENT_PROVIDER == "":
                        CONTENT_PROVIDER = CreditsItem.findtext( "{%s}OrganizationName" % rootNS )
                    else:
                        print 'Found content item with two content providers!'
                        print ET.tostring(pi)
                        sys.exit(900)
                if "role" in CreditsItem.attrib and  CreditsItem.attrib["role"].endswith('CONTENT-PROVIDER-ID'):
                    if CONTENT_PROVIDER_ID == "":
                        CONTENT_PROVIDER_ID = CreditsItem.findtext("{%s}OrganizationName" % rootNS )
                    else:
                        print 'Found content item with two content provider ids!'
                        print ET.tostring(pi)
                        sys.exit(900)
        if child.tag.endswith('Genre'):
            if child.attrib.get('type') == 'main':
                href =  child.attrib.get('href')
                if 'UPCEventGenreCS:2009' in href:
                    _2009genre = 1
                    mainGenre = href[href.rfind(':')+1:]
                elif 'DvbContentNibblesCS:2011' in child.attrib.get('href'):
                    backupGenre =  href[href.rfind(':')+1:]
                    _2011genre = 1
        elif child.tag.endswith('RelatedMaterial'):
            HowRelated=child.find( "{%s}HowRelated" % rootNS )
            if HowRelated is not None and "href" in HowRelated.attrib:
                href=HowRelated.attrib["href"]
                if href == "urn:eventis:metadata:cs:HowRelatedCS:2010:33.1":
                    HasPreview = child.findtext("{%s}MediaLocator/{%s}MediaUri" % ( rootNS, 'urn:tva:mpeg7:2008' ))
                elif href == "urn:eventis:metadata:cs:HowRelatedCS:2010:33.2":
                    IsPreviewOf = child.findtext("{%s}MediaLocator/{%s}MediaUri" % ( rootNS, 'urn:tva:mpeg7:2008' ))
    if mainGenre == None:
         #print 'Found program with no main genre'
         #print 'processProgramInformation: ' + ET.tostring(pi)
        mainGenre = '00'


    # create and store ContentDetails named tuple(program_crid series_crid mainGenre)
    contentDetails = ContentDetails(crid, EpisodeOf, mainGenre, HasPreview, IsPreviewOf)
    parsedPrograms[crid] = contentDetails

    # store CONTENT_PROVIDER and CONTENT_PROVIDER_ID for OnDemand program write-out
    if CONTENT_PROVIDER != "" or CONTENT_PROVIDER_ID.encode != "":
        programCrid2ContentProviderMap[crid] = (CONTENT_PROVIDER.encode('utf8'), CONTENT_PROVIDER_ID.encode('utf8') )

    # Process Titles
    # construct TitleDetails tuples (program_crid title_type title_language title) aand write using titleWriter
    title = basicDesc.findtext("{%s}Title" % rootNS )
    titles = basicDesc.findall("{%s}Title" % rootNS )
    for title in titles:
        writeTitle(title, crid, xmlNS, TitleDetails, allWrittenTitles,titleTuple, titleWriter)
    return
    #programDictionary[crid] = (title, mainGenre, EpisodeOf, SeriesName)
     #if len(mainGenreList) > 1:
         #print 'Genre list ---'
         #for pp in  mainGenreList:
             #print pp.encode('utf8')
