from parseTVA_common import writeTitle
from parseTVA_common import durationStringToSeconds
from parseTVA_common import getWriter
from parseTVA_processProgramInformation import processProgramInformation
from parseTVA_processSchedule import processScheduleEvent
from parseTVA_processSchedule import processSchedule
from parseTVA_processServiceInformation import processServiceInformation
from parseTVA_processBroadcastEvent import processBroadcastEvent
from parseTVA_processOnDemandProgram import processOnDemandProgram
from parseTVA_processProduct import processProduct
from parseTVA_processSeries import processSeries


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

"""
    ------ create path if needed
"""
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# create output root if needed
ensure_dir(output_root)

# create PROGRAM_INFORMATION output folder

program_information_path = output_root + 'PROGRAM_INFORMATION/' + country_code + '/' + process_date
ensure_dir(program_information_path)
ensure_dir(program_information_path + '/titles')
programInfoFilePath = program_information_path + '/' + country_code + 'content'  + process_date + '.tsv'
programInfoFTitleFilePath = program_information_path + '/titles' +  '/' + country_code + 'titles'  + process_date + '.tsv'

# create SCHEDULE ouptut folder
scheduleDirName = output_root + 'SCHEDULE/country_' + country_code + '/'
ensure_dir(scheduleDirName)

# create ON_DEMAND output folder
onDemandDir =  output_root + 'ON_DEMAND_PROGRAM/country_' + country_code + '/'
ensure_dir(onDemandDir)
onDemandPath = onDemandDir + country_code + 'onDemand'  + process_date + '.tsv'

# create VOD_PRODUCT output folder
vodProductDir =  output_root + 'VOD_PRODUCT/country_' + country_code + '/' 
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
        titleTuple = TitleDetails
        processProgramInformation(program, referencedSeriesCrids, programCrid2ContentProviderMap, parsedPrograms, rootNS, ContentDetails, xmlNS, TitleDetails, allWrittenTitles, titleTuple, titleWriter)

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
        schedEventCount = schedEventCount + processSchedule(channelSchedule, serviceID2DVB, rootNS, process_date)

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
            processSeries(groupItem, groupCrid, seriesTitleMap, xmlNS, allWrittenTitles,titleTuple,titleWriter)
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
