#import tva_util

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
# tuple of "ProgramCrid", "ProductCrid" stored in dictionary of "VodBackOfficeId (i.e. assetID) -> ("ProgramCrid", "ProductCrid")
OnDemandProgramDetails=namedtuple("OnDemandProgramDetails", "ProgramCrid ProductCrid")

# Named tuple to produce record for
# tva_program_information_staging
#   program_crid STRING,
#   series_crid STRING,
#   mainGenre string,
#   duration_in_seconds string
# we retrieve the duration later (where possible) so just the first 3 in the tuple parsed from ProgramInformation
ContentDetails=namedtuple("ContentDetails", "program_crid series_crid mainGenre HasPreview IsPreviewOf") 
# Named tulple to hold title record. Named tuple ensures all calls to writer output same fields
# Title type values are "main", "episodeTitle", "seriesTitle" 
#    program_crid STRING,
#    title_type   STRING,
#    title_language STRING,
#    title       STRING
TitleDetails=namedtuple("TitleDetails", "program_crid title_type title_language title")


DvbTriple = namedtuple('DvbTriple', 'networkid transponderid siserviceid,channelName')


# Named tulple to hold BroadcastEvent broadcast details
BroadcastDetails=namedtuple("BroadcastDetails", "PublishedStartTime PublishedEndTime PublishedDuration dvbTriple")


try:
    from html import escape  # py3
except ImportError:
    from cgi import escape  # py2


# write a title element out for program identified by crid. Element type passed in for debug messages
def writeTitle(title, crid):
    lang = ""
    if "{%s}lang" %xmlNS in title.attrib:
        lang=title.attrib.get("{%s}lang" %xmlNS )
    else:
        print "Found title with no language attribute", ET.tostring(title)
        return;
        
    if  title.text == None or title.text == "":
        print "Null title in ", ET.tostring(title), "for crid ", crid
        return
    titleText = title.text.encode('utf8').replace('\n', ' ').replace('\r', '')
    if 'type' in title.attrib:
        titleType =  title.attrib['type']
    else:
        titleType = 'main'
    titleTuple = TitleDetails(crid,  titleType, lang, titleText)
    # only output each crit / titleType once
    if (crid,  titleType, lang) not in allWrittenTitles:
        titleWriter.writerow ( titleTuple)
        allWrittenTitles.add( (crid,  titleType, lang) )


# Convert strings like P1DT1H30M or PT30M5S to seconds
def durationStringToSeconds(durationString):
    duration_seconds = 0
    regex_str = r"P(?:(\d)+D)?T(?:(\d)+H)?(?:(\d+)M)?(?:(\d+)S)?"
    try:
        m = re.search(regex_str, durationString)
        if m != None:
            if m.group(1) != None :
                duration_seconds = duration_seconds + int(m.group(1)) * 3600 * 24
            if m.group(2) != None :
                duration_seconds = duration_seconds + int(m.group(2)) * 3600
            if m.group(3) != None :
                duration_seconds = duration_seconds + int(m.group(3)) * 60
            if m.group(4) != None :
                duration_seconds = duration_seconds + int(m.group(4))
       # print "duration_seconds", duration_seconds
        return duration_seconds
    except:
        return -1

"""
    get a csv writer for the end date passed in
"""
def getWriter(endDate):

    # check if date way outside range?
    process_date_date = datetime.datetime.strptime(process_date, '%Y-%m-%d')
    endDate_date = datetime.datetime.strptime(endDate, '%Y-%m-%d')
    diff = (endDate_date - process_date_date ).days

    # print "In get writer - endDate %s, process_date %s diff %d" %(endDate, process_date, diff)
    if diff < -1 or diff > 30:
        return None

    if endDate in scheduleWriters:
        return scheduleWriters[endDate]

    scheduleFilename = scheduleDirName + country_code + 'schedule' + endDate + '.csv'

    scheduleFile = open(scheduleFilename,'w')
    scheduleWriter =  csv.writer(scheduleFile, delimiter='\t')
    scheduleWriters[endDate] = scheduleWriter
    return scheduleWriter


"""
    processProgramInformation - create a dictionary of program details
    takes a programInformation element
    adds a ContentDetails tuple to parsedPrograms
    records the referenced SeriesCrid if any in referencedSeriesCrids
    records the ContentProvider info if any in programCrid2ContentProviderMap
    writes out any titles to titleWriter
"""
def processProgramInformation(pi, referencedSeriesCrids, programCrid2ContentProviderMap, parsedPrograms):

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
        writeTitle(title, crid)
    return
    #programDictionary[crid] = (title, mainGenre, EpisodeOf, SeriesName)
     #if len(mainGenreList) > 1:
         #print 'Genre list ---'
         #for pp in  mainGenreList:
             #print pp.encode('utf8')


"""   Process Schedlule Event - write a row for a scheduled program for a channel
      ------------- 
"""  
def processScheduleEvent(se, dummyName):

   #   print 'processScheduleEvent: ' + ET.tostring(se)


    # print 'Starttime',  se.findtext(  "{%s}PublishedStartTime" % rootNS  ).replace('T', ' ').replace('Z','')
    # print 'EndTime', se.findtext(  "{%s}PublishedEndTime" % rootNS  )
    # print 'PublishedDuration', se.findtext(  "{%s}PublishedDuration" % rootNS  )

# regex to match the time duration string
# Formates are iso duration format, in minutes or hours and minutes
# i.e. PT10M or PT5H45M or PT1H
    duration_seconds = durationStringToSeconds( se.findtext(  "{%s}PublishedDuration" % rootNS  ))
    

# regex to match the DVB triple
# Source is of the form <ProgramURL>dvb://0600.083a.7764;867b~20140809T124500Z--PT5H45M</ProgramURL>
    dvb_regex = r"dvb://([0-9A-Fa-f]+)\.([0-9A-Fa-f]+)\.([0-9A-Fa-f]+);"
    # print "ProgramURL =" ,  se.findtext(  "{%s}ProgramURL" % rootNS)
    m = re.search(dvb_regex,  se.findtext(  "{%s}ProgramURL" % rootNS  ))
    
    ServiceId = int(m.group(1), 16)
    TransportId =  int(m.group(2), 16)
    NetworkId =  int(m.group(3), 16)

    # print 'ServiceId', ServiceId
    # print 'TransportId', TransportId
    # print 'NetworkId', NetworkId

    endDate = se.findtext(  "{%s}PublishedEndTime" % rootNS  ).replace('T', ' ').replace('Z','')[0:10]
    scheduleWriter = getWriter(endDate)
    if scheduleWriter:
        crid =  se.find( "{%s}Program" % rootNS ).attrib.get('crid')
        scheduleWriter.writerow((
            se.findtext(  "{%s}PublishedStartTime" % rootNS  ).replace('T', ' ').replace('Z','') # 'PublishedStartTime'
            , se.findtext(  "{%s}PublishedEndTime" % rootNS  ).replace('T', ' ').replace('Z','') # 'PublishedEndTime'
            , duration_seconds # 'PublishedDuration'
            , crid# 'crid'
            , NetworkId # 'networkid'
            , TransportId # 'transponderid'
            , ServiceId # 'serviceid'
            , process_date # 'fileDate'
            , se.findtext( "{%s}InstanceMetadataId" % rootNS )
        ))
        # store the duration to put into the program table
        programDurations[crid] = duration_seconds
    return DvbTriple(NetworkId, TransportId, ServiceId, dummyName)
 #  checking how many are referenced - no need to keep doing
  #   prog = programDictionary[crid]
  #   print 'found program details', prog
  #   programDictionary[crid] = (prog[0], prog[1], prog[2] + 1)

    

    



"""
    ----- Process a whole schedule for a linear channel
"""
def processSchedule(sched, serviceID2DVB):
   # print 'Processing schedule for ', sched.attrib.get('serviceIDRef'), sched.attrib.get('start'), '-', sched.attrib.get('end')
    schedEventCount = 0
    serviceId = ""
    dummyName = ""
    if 'serviceIDRef' in sched.attrib:
        serviceId = sched.attrib['serviceIDRef']
        dummyName = "dummy " + serviceId
    for child in sched:
        if child.tag.endswith( 'ScheduleEvent'):
            dvb = processScheduleEvent(child, dummyName)
            if serviceId != "":
                serviceID2DVB[serviceId] = dvb
                serviceId = "" # just use the first dvb
            schedEventCount = schedEventCount + 1
    return schedEventCount

"""
    Parse /ServiceInformation entries
    populate map of ServiceId -> dvbTriple
"""
def processServiceInformation (service,serviceID2DVB ):
    if 'serviceId' in service.attrib:
        serviceId = service.attrib['serviceId']
        newDvb = None
        channelName = service.findtext( "{%s}Name" % rootNS)
        if serviceId == "Disney_Channel_HD":
            print "See Disney_Channel_H in processServiceInformation"
        for genre in service.findall( "{%s}ServiceGenre" % rootNS):
            if genre.findtext( "{%s}Name" % rootNS) == "CableLocator":
                dvb = genre.findtext( "{%s}Definition" % rootNS) 
                if serviceId == "Disney_Channel_HD":
                    print "found dvb", dvb
                print dvb
                # get DVB triples where possible
                #dvb_regex = r"dvb://([0-9A-Fa-f]+)\.([0-9A-Fa-f]+)\.([0-9A-Fa-f]+)"
                dvb_regex = r"dvb://([0-9A-Fa-f]+)[\.:]([0-9A-Fa-f]+)[\.:]([0-9A-Fa-f]+)"
                m = re.search(dvb_regex,  dvb )
                if m is not None:
                        
                    ServiceId = int(m.group(1), 16)
                    TransportId =  int(m.group(2), 16)
                    NetworkId =  int(m.group(3), 16)
                    newDvb = DvbTriple(NetworkId, TransportId, ServiceId, channelName)
                    #serviceID2DVB[serviceId] = DvbTriple(NetworkId, TransportId, ServiceId, channelName)
                    if serviceId == "Disney_Channel_HD":
                        print "Set", serviceID2DVB[serviceId]
        if serviceId in serviceID2DVB:
            scheduleDVB = serviceID2DVB[serviceId]
            print "Found ServiceInformation for existing channel", serviceId
            print "Schedule dvb  ", scheduleDVB
            if newDvb != None:
                print "ServiceInfo dvb", newDvb
                if scheduleDVB.networkid != newDvb.networkid or scheduleDVB.transponderid != newDvb.transponderid or  scheduleDVB.siserviceid != newDvb.siserviceid:
                    print "DANGER WILL ROBINSON - DVB doesn't match"
                serviceID2DVB[serviceId] = newDvb
            else:
                serviceID2DVB[serviceId] = DvbTriple( scheduleDVB.networkid,  scheduleDVB.transponderid, scheduleDVB.siserviceid, channelName)
                print "Build new dvb", serviceID2DVB[serviceId]
                
        else:
            print "Found new channel not in schedule", serviceId, channelName
            if newDvb != None:
                print "Adding " , newDvb
                serviceID2DVB[serviceId] = newDvb
            else:
                print "Count not find dvb for ", serviceId

"""
    Parse BroadcastEvent element
    add entry to assetId2BroadcastDetails 
      assetId -> (start, end, duration)
        PublishedStartTime is not always populated - if not compute
"""
def processBroadcastEvent(broadcastEvent, assetId2BroadcastDetails, serviceID2DVB):
    otherIdentifiers = broadcastEvent.findall("{%s}InstanceDescription/{%s}OtherIdentifier" % (rootNS, rootNS) )
    assetId = ''
    for id in otherIdentifiers:
        if "type" in id.attrib:
            if id.attrib["type"] == "VodBackOfficeId":
                assetId = id.text
    if assetId == '':
        return

    startTime=broadcastEvent.findtext("{%s}PublishedStartTime" % rootNS)
    endTime=broadcastEvent.findtext("{%s}PublishedEndTime" % rootNS)
    duration=broadcastEvent.findtext("{%s}PublishedDuration" % rootNS)

    if startTime is None or startTime == '':
        print "No startTime for BroadcastEvent"
        return ET.tostring(broadcastEvent)
    if (endTime is None or endTime == '') and (duration is None or duration  == '') :
        print "No endTime or duration for BroadcastEvent"
        return ET.tostring(broadcastEvent)
        return

    duration_seconds = durationStringToSeconds(duration)

    startTimeSeconds =  calendar.timegm(time.strptime(startTime, '%Y-%m-%dT%H:%M:%SZ'))
    if endTime is not None and endTime != "":
        endTimeSeconds =  calendar.timegm(time.strptime(endTime, '%Y-%m-%dT%H:%M:%SZ'))
        if endTimeSeconds !=  startTimeSeconds + duration_seconds:
            print "endTimeSeconds !=  startTimeSeconds + duration_seconds"
            print ET.tostring(broadcastEvent)
    else:
        endTimeSeconds = startTimeSeconds + duration_seconds

    dvbTriple = None
    # get serviceId from attribute, look for dvb details
    if 'serviceIDRef' in broadcastEvent.attrib:
        serviceIDRef = broadcastEvent.attrib['serviceIDRef']
        if serviceIDRef == 'Disney_Channel_HD':
            print "Found broadcastEvent for Disney_Channel_HD"
            print " serviceIDRef in serviceID2DVB",  serviceIDRef in serviceID2DVB
        if serviceIDRef in serviceID2DVB:
            dvbTriple = serviceID2DVB[serviceIDRef]
            

    
    assetId2BroadcastDetails[assetId] = BroadcastDetails(startTimeSeconds, endTimeSeconds, duration_seconds, dvbTriple)

"""
    ----- Process an OnDemandProgram tag - a vod instance detail
"""
def processOnDemandProgram(OnDemandProgram, referencedProductCrids, programCrid2ContentProviderMap,  programDurations):
        # we want to fine InstanceDescription/OtherIdentifier type="VodBackOfficeId"
    #print "Processing OnDemandProgram"
    #print  ET.tostring(OnDemandProgram)

    program = OnDemandProgram.find(  "{%s}Program" % rootNS  )
    programCrid = program.attrib.get('crid')
    #print "Found programCrid"
    #print programCrid
    VodBackOfficeId = ""
    productId = None

    InstanceDesc = OnDemandProgram.find(  "{%s}InstanceDescription" % rootNS  )
    for child in InstanceDesc:
        if child.tag.endswith('OtherIdentifier'):
            if child.attrib.get('type') == 'VodBackOfficeId':
                VodBackOfficeId =  child.text
        elif child.tag.endswith('MemberOf'):
            if child.attrib.get("{%s}type" % xsiNS) == "MemberOfType":
                productId =  child.attrib.get('crid')
                referencedProductCrids.add(productId)

    if productId is None :
        print "OnDemand Program with no product"
        print ET.tostring(OnDemandProgram)
        return
        onDemandWithoutProduct += 1
        sys.exit(-1)
        

    # get PublishedDetils for catch up TV
    publishedStartTime = ''
    publishedEndTime = ''
    publishedDuration = ''
    NetworkId = ''
    TransponderId = ''
    ServiceId = ''
    channelName = ''

    if VodBackOfficeId != "":
        # only write each once
        if (productId, VodBackOfficeId) in  onDemandAssetProducts:
            return
        else:
            onDemandAssetProducts.add( (productId, VodBackOfficeId) ) ;
        if VodBackOfficeId in assetId2BroadcastDetails:
            broadcastDetails = assetId2BroadcastDetails[VodBackOfficeId]
            publishedStartTime = broadcastDetails.PublishedStartTime
            publishedEndTime = broadcastDetails.PublishedEndTime
            publishedDuration =  broadcastDetails.PublishedDuration
            dvb = broadcastDetails.dvbTriple
            if dvb is not None:
                NetworkId = dvb.networkid 
                TransponderId = dvb.transponderid
                ServiceId = dvb.siserviceid
                channelName = dvb.channelName


        if programCrid in programCrid2ContentProviderMap:
            cpTuple = programCrid2ContentProviderMap[programCrid]
            contentProvider = cpTuple[0]
            contentProviderId = cpTuple[1]
        else:
            contentProvider = ""
            contentProviderId = ""
        try:
            onDemandWriter.writerow ((
                    VodBackOfficeId,
                    productId,
                    programCrid,
                    contentProvider,
                    contentProviderId,
                    publishedStartTime,
                    publishedEndTime,
                    publishedDuration,
                    NetworkId,
                    TransponderId,
                    ServiceId
                    #, channelName
                    ))
            
            duration_seconds = durationStringToSeconds( OnDemandProgram.findtext(  "{%s}PublishedDuration" % rootNS  ))
            programDurations[programCrid] = duration_seconds
        except:
            print "exception pritning OnDemand element ", VodBackOfficeId
            print "contentProvider" , contentProvider
            print "contentProviderId", contentProviderId

def processProduct(groupItem):
    groupCrid = groupItem.attrib.get('groupId')
    title = None
    basicDesc = groupItem.find(  "{%s}BasicDescription" % rootNS  )
    #print "------"
    #print "VOD product {%s}" % groupCrid
    if basicDesc:
        shortSynopsis = ''
        longSynopsis = ''
        title = basicDesc.findtext("{%s}Title" % rootNS)
        #print "found {%s} as title by findtext" % title
        
        for Synopsis in  basicDesc.findall("{%s}Synopsis" %  rootNS):
            if "length" in Synopsis.attrib:
                synLength = Synopsis.attrib["length"]
                if synLength == 'short':
                    shortSynopsis = Synopsis.text
                elif synLength == 'long':
                    longSynopsis = Synopsis.text
    else:
        print "Could not find Basic Description for GroupInformation " , groupCrid, "which should be a VOD product"
        return

    VodBackOfficeId=''
    SUBSCRIPTION_PACKAGE_ID=''
    for child in groupItem:
        if child.tag.endswith('OtherIdentifier'):
            type = child.attrib.get('type')
            if type == 'VodBackOfficeId':
                VodBackOfficeId =  child.text
            elif type == "SUBSCRIPTION_PACKAGE_ID":
                SUBSCRIPTION_PACKAGE_ID = child.text

    # Get base VOD type from 
    #   <BasicDescription ...
    #   ...
    #     <PurchaseList>
    #       <PurchaseItem start="2009-01-01T00:00:00Z" end="2030-12-31T23:59:59Z">
    #         <Price currency="EUR">0</Price>
    #         <Purchase>
    #            <PurchaseType href="urn:eventis:metadata:cs:PurchaseTypeCS:2010:opportunity.subscription">
    vod_type = ""
    vod_type_element = basicDesc.find("{%s}PurchaseList/{%s}PurchaseItem/{%s}Purchase/{%s}PurchaseType"  % (rootNS, rootNS, rootNS, rootNS))
    if vod_type_element:
        href = vod_type_element.attrib['href']
        if href: 
            vod_type = href.rsplit('.',1)[-1]

    # Get (possibly 2)  parental guidance codes from 
    #     <ParentalGuidance>
    #       <ParentalRating xmlns="urn:tva:mpeg7:2008" href="urn:tva:metadata:cs:UPCAgeRatingCS:2008:1">
    #         <Name xml:lang="en-IE">PG</Name>
    #       </ParentalRating>
    #     </ParentalGuidance>
    #     <ParentalGuidance>
    #       <ParentalRating xmlns="urn:tva:mpeg7:2008" href="urn:eventis:metadata:cs:AgeCS:2010:4">
    #         <Name xml:lang="en-IE">Minimum age 4</Name>
    #       </ParentalRating>
    #     </ParentalGuidance>
    UPCAgeRatingCS_2008=""
    AgeCS_2010=""
    for ParentalGuidance in basicDesc.findall("{%s}ParentalGuidance" % rootNS):
        ParentalRating = ParentalGuidance.find("{%s}ParentalRating" % rootNS)
        if len(ParentalGuidance) > 0 and ParentalGuidance[0].tag.endswith('ParentalRating'):
            href = ParentalGuidance[0].attrib['href']
            #print "ParentalRating href %s" % href
            if href:
                if href.startswith("urn:tva:metadata:cs:UPCAgeRatingCS:2008"):
                    UPCAgeRatingCS_2008 = href.rsplit(':',1)[-1]
                elif href.startswith("urn:eventis:metadata:cs:AgeCS:2010"):
                    AgeCS_2010 = href.rsplit(':',1)[-1]
    #print "UPCAgeRatingCS_2008 {%s}" % UPCAgeRatingCS_2008
    #print "AgeCS_2010 %s" % AgeCS_2010
        
    # get Provider from
    #   <BasicDescription ...
    #   ...
    #        <CreditsList>
    #        <CreditsItem role="urn:eventis:metadata:cs:RoleCS:2010:PROVIDER">
    #          <OrganizationName xml:lang="en-IE">Arrivo</OrganizationName>
    #        </CreditsItem>
    #      </CreditsList>
    # can't use ful xpath to element as attribute only in elementree shipped with python 2.7 
    provider = ""
    creditItems = basicDesc.findall("{%s}CreditsList/{%s}CreditsItem" % (rootNS, rootNS) )
    for creditItem in creditItems:
        if "role" in creditItem.attrib:
            if creditItem.attrib["role"] == "urn:eventis:metadata:cs:RoleCS:2010:PROVIDER":
                provider = creditItem.findtext("{%s}OrganizationName" % rootNS)
    provider = provider.encode('utf8')
    #print "provider {%s}" % provider 

    
#groupCrid
#VodBackOfficeId
 #UPCAgeRatingCS_2008=""
    #AgeCS_2010=""
#provider
#title.encode('utf8')

# PRODUCT_CRID
# PRODUCT_TITLE
# PRODUCT_SYNOPSIS short
# PRODUCT_SYNOPSIS long
# PARENTAL_GUIDE UPCAgeRatingCS_2008
# PARENTAL_GUIDE AgeCS_2010
# CAS_CODE  ? SUBSCRIPTION_PACKAGE_ID
# SEACHANGE_CODE
# PROVIDER_ID
# VOD_TYPE



    vodProductWriter.writerow((
            groupCrid,
            title.encode('utf8'),
            shortSynopsis.encode('utf8').replace('\n', ' ' ),
            longSynopsis.encode('utf8').replace('\n', ' ' ),
            UPCAgeRatingCS_2008,
            AgeCS_2010,
            SUBSCRIPTION_PACKAGE_ID.encode('utf8'),
            VodBackOfficeId,
            provider.encode('utf8'),
            vod_type.encode('utf8')
        ))

"""
    ----- Process the series group - just write the title per series crid - we will join later on to tva_content
"""

def processSeries(series, groupCrid, seriesTitleMap):
        # we want to output series crid and title (tab seperated)

    seriesCrid = series.attrib.get('groupId')
    basicDesc = series.find(  "{%s}BasicDescription" % rootNS  )
    titles = basicDesc.findall("{%s}Title" % rootNS )
    for title in titles:
        writeTitle(title, seriesCrid)

"""
    ------ create path if needed
"""
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
"""
   ------------------------------------------------------------
   -------------------      Main      -------------------------
   ------------------------------------------------------------
"""



if  len(sys.argv) >= 5:
    country_code = sys.argv[1]
    process_date = sys.argv[2]
    inputFile =   sys.argv[3]
    output_root =  sys.argv[4]
else:
    print 'parseTVA.py must be called with Country, yyyy-mm-dd inputFile, output_root'
    sys.exit(-1)

print datetime.datetime.now(), 'parseTVA.py', country_code, process_date, inputFile, output_root

# check input file
if not os.path.exists(inputFile):
    print 'input file', inputFile, 'does not exist'
    sys.exit(-1)

# create output root if needed
ensure_dir(output_root)

# create PROGRAM_INFORMATION output folder

program_information_path = output_root + '/PROGRAM_INFORMATION/' + country_code + '/' + process_date
ensure_dir(program_information_path)
ensure_dir(program_information_path + '/titles')
programInfoFilePath = program_information_path + '/' + country_code + 'content'  + process_date + '.tsv'
programInfoFTitleFilePath = program_information_path + '/titles' +  '/' + country_code + 'titles'  + process_date + '.tsv'

# create SCHEDULE ouptut folder
scheduleDirName = '/home/bigdata/group/videorep/audience_measurement/data/tva/SCHEDULE/country_' + country_code + '/'
ensure_dir(scheduleDirName)

# create ON_DEMAND output folder
onDemandDir =  '/home/bigdata/group/videorep/audience_measurement/data/tva/ON_DEMAND_PROGRAM/country_' + country_code + '/'
ensure_dir(onDemandDir)
onDemandPath = onDemandDir + country_code + 'onDemand'  + process_date + '.tsv'

# create VOD_PRODUCT output folder
vodProductDir =  '/home/bigdata/group/videorep/audience_measurement/data/tva/VOD_PRODUCT/country_' + country_code + '/' 
ensure_dir(vodProductDir)
vodProductPath = vodProductDir + country_code + 'vodProduct' + process_date + '.tsv'


import xml.etree.cElementTree as ET
parse_start = time.time()

 ########################
 #    Parse file
 ########################

xT = ET.parse(inputFile)
root=xT.getroot()
rootNS = 'urn:tva:metadata:2010' 
xmlNS = 'http://www.w3.org/XML/1998/namespace'
xsiNS= "http://www.w3.org/2001/XMLSchema-instance"


print "Parsed new TVA file in %s seconds " % (time.time() - parse_start) 

print "Opening programInfoFile at ", programInfoFilePath
print "Opening programInfoFTitleFilePath at ", programInfoFTitleFilePath
programInfoFile = open(programInfoFilePath, 'w')
programWriter = csv.writer(programInfoFile, delimiter='\t')

programTitleFile = open(programInfoFTitleFilePath, 'w')
titleWriter = csv.writer(programTitleFile,  delimiter='\t', quoting=csv.QUOTE_NONE, escapechar = '\\')
processed_referencedProductCrids = set()
processed_referencedSeriesCrids = set()




 ########################
 #    Read programs
 ########################
# only output each crit / titleType once
allWrittenTitles = set()

referencedSeriesCrids = set()
programCrid2ContentProviderMap = {}
parsedPrograms = {} # map of crid -> program details (list) to add series title to
programDurations = {} # map of crid -> program duration - to fill in (hopefully) from Schedule and OnDemand programs
prog_start = time.time()
print 'Processing ProgramInformationTable'
sstring = "{%s}ProgramDescription/{%s}ProgramInformationTable" % (rootNS,rootNS)
ProgramInformationTable = xT.getroot().find(sstring)
for program in ProgramInformationTable:
    if program.tag.endswith('ProgramInformation'):
        processProgramInformation(program, referencedSeriesCrids, programCrid2ContentProviderMap, parsedPrograms)

#tva_util.storeProgramDictionary(country_code, process_date,programDictionary)


print "Saw refereces to %s series" % len(referencedSeriesCrids)


 ########################
 #    Read Schedules just to get ServiceID -> dvb
 ########################
print "Reading BroadcastEvent program information "
serviceID2DVB = {}  # map of serviceID to dvbTriple (with channel name)
sstring = "{%s}ProgramDescription/{%s}ProgramLocationTable" % (rootNS,rootNS)
ProgramLocationTable = xT.getroot().find(sstring)

sched_start = time.time()
scheduleWriters = {}
# shouldn't have to do this every time ProgramLocationTable = xT.getroot().find(sstring)
# check the children of the ProgramLocationTable
# should have Schedule, BroadcastEvent and OnDemandProgram
sched_count = 0
schedEventCount = 0
for channelSchedule in ProgramLocationTable:
    if channelSchedule.tag.endswith('Schedule'):
         # print "calling processSchedule ", channelSchedule.tag
        schedEventCount = schedEventCount + processSchedule(channelSchedule, serviceID2DVB)

print "Ouput %d schedule records for %d channels in %s seconds " %  ( schedEventCount, sched_count, (time.time() - sched_start)) 



 ########################
 #    Read ServiceInformation table to get dvb triples to put into BroadcastEvents by serviceId
 ########################
print "Reading ServiceInformationTable"
sstring = "{%s}ProgramDescription/{%s}ServiceInformationTable" % (rootNS,rootNS)
ServiceInformationTable = xT.getroot().find(sstring)
Services = ServiceInformationTable.findall("{%s}ServiceInformation" % rootNS)
for service  in Services:
    processServiceInformation(service, serviceID2DVB)
print "Found", len(serviceID2DVB), "dvb triples"


 ########################
 #    Read BroadcastEvent records to store broadcast time
 ########################
print "Reading BroadcastEvent program information "
assetId2BroadcastDetails = {}  # map of VOD asset id to BroadcastDetails named tupple
sstring = "{%s}ProgramDescription/{%s}ProgramLocationTable" % (rootNS,rootNS)
ProgramLocationTable = xT.getroot().find(sstring)
# check the children of the ProgramLocationTable
# should have Schedule, BroadcastEvent and OnDemandProgram
for broadcastEvent in ProgramLocationTable.findall("{%s}BroadcastEvent" % rootNS):
    processBroadcastEvent(broadcastEvent, assetId2BroadcastDetails, serviceID2DVB)

print "Found " , len(assetId2BroadcastDetails) , " assets with BroadcastDetails"

 ########################
 #    Read OnDemandPrograms
 ########################
print "Reading OnDemand program information "
print "Opening onDemandWriter at", onDemandPath
onDemandFile = open(onDemandPath ,'w')
onDemandWriter = csv.writer(onDemandFile, delimiter='\t') 

referencedProductCrids = set()  #keep set of products to expect in GroupInformation
onDemandAssetProducts = set () # only put each on demand program (assetID, productID) pair out once
repeatedAssetIdCount = 0
onDemandWithoutProduct = 0
# TODO load old copy of OnDemand Programs

#print 'Processing OnDemandProgram elements'
# should only have to do this once sstring = "{%s}ProgramDescription/{%s}ProgramLocationTable" % (rootNS,rootNS)
# should only have to do this once ProgramLocationTable = xT.getroot().find(sstring)
# check the children of the ProgramLocationTable
# should have Schedule, BroadcastEvent and OnDemandProgram
for OnDemandProgram in ProgramLocationTable:
    if OnDemandProgram.tag.endswith('OnDemandProgram'):
        #print "Found OnDemandProgram"
        processOnDemandProgram(OnDemandProgram, referencedProductCrids, programCrid2ContentProviderMap,  programDurations)

print "Found " , len(referencedProductCrids) , " references to product crids"
#print "Found", repeatedAssetIdCount, "repeatedAsset Ids"
  ######
print "Found ", onDemandWithoutProduct, " OnDemand programs with no product"




########################
#    Read SeriesGroups
########################

seriesTitleMap = {} # map of series crid to titles list

print "Opening vodProductFile at ", vodProductPath
vodProductFile = open(vodProductPath ,'w')
vodProductWriter = csv.writer(vodProductFile, delimiter='\t') 

sstring = "{%s}ProgramDescription/{%s}GroupInformationTable" % (rootNS,rootNS)
GroupInformationTable = xT.getroot().find(sstring)
series_count = 0
product_count = 0
for groupItem in GroupInformationTable:
    groupType = groupItem.find("{%s}GroupType" % rootNS)
    #print ET.tostring(groupItem)
    #if product_count > 10:
        #sys.exit(2)
    if groupType != None:
        groupTypeType = groupType.attrib.get("{%s}type" % xsiNS)
        groupTypeValue = groupType.attrib.get("value")
    if (groupTypeType == "ProgramGroupTypeType"): ###  and groupTypeValue == "series"):
        groupCrid = groupItem.attrib.get('groupId')
        if groupCrid in referencedProductCrids:
            referencedProductCrids.remove(groupCrid)
            processed_referencedProductCrids.add(groupCrid)
            processProduct(groupItem)
            product_count += 1
        elif groupCrid in processed_referencedProductCrids:
            print "DANGER - group", groupCrid, " appears twice in GroupInformationTable"
        elif groupCrid in referencedSeriesCrids:
            processSeries(groupItem, groupCrid, seriesTitleMap)
            referencedSeriesCrids.remove(groupCrid)
            processed_referencedSeriesCrids.add(groupCrid)
        elif groupCrid in processed_referencedProductCrids:
            print "DANGER - Product crid appears more than once in the GroupInformationTable", groupCrid, " appears twice in GroupInformationTable"
        #processSeries(groupItem, newSeries)

print "Unfound products", len(referencedProductCrids)
print "Found products", len(processed_referencedProductCrids)

print "Unfound series", len(referencedSeriesCrids)
print "Found series", len(processed_referencedSeriesCrids)

######### Process parsed programs, add series title and write out
foundSeries=False
for crid in parsedPrograms:
    programDetails = parsedPrograms[crid]
    # add series title
    if crid in programDurations:
        durationInSeconds = programDurations[crid]
    else:
        durationInSeconds = -2
    programWriter.writerow(( programDetails.program_crid ,programDetails.series_crid, programDetails.mainGenre, durationInSeconds, programDetails.HasPreview,  programDetails.IsPreviewOf))
 

print "Written programs - python finishing"
