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

# write a title element out for program identified by crid. Element type passed in for debug messages
def writeTitle(title, crid, xmlNS, TitleDetails, allWrittenTitles, titleTuple, titleWriter):
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
        titleWriter.writerow (titleTuple)
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
def getWriter(endDate, process_date):

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




