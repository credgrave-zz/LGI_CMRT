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