from parseTVA_common import durationStringToSeconds
from parseTVA_common import getWriter

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
    ----- Process a whole schedule for a linear channel
"""
def processSchedule(sched, serviceID2DVB, rootNS, process_date):
   # print 'Processing schedule for ', sched.attrib.get('serviceIDRef'), sched.attrib.get('start'), '-', sched.attrib.get('end')
    schedEventCount = 0
    serviceId = ""
    dummyName = ""
    if 'serviceIDRef' in sched.attrib:
        serviceId = sched.attrib['serviceIDRef']
        dummyName = "dummy " + serviceId
    for child in sched:
        if child.tag.endswith( 'ScheduleEvent'):
            dvb = processScheduleEvent(child, dummyName, rootNS, process_date)
            if serviceId != "":
                serviceID2DVB[serviceId] = dvb
                serviceId = "" # just use the first dvb
            schedEventCount = schedEventCount + 1
    return schedEventCount

"""   Process Schedlule Event - write a row for a scheduled program for a channel
      ------------- 
"""  
def processScheduleEvent(se, dummyName, rootNS, process_date):

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
    scheduleWriter = getWriter(endDate, process_date)
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

    

    

