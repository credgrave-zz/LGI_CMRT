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
