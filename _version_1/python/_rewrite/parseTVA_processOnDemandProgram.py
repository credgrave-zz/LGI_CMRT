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
