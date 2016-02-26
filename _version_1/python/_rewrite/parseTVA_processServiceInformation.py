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
