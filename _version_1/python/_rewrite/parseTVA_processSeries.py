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
    ----- Process the series group - just write the title per series crid - we will join later on to tva_content
"""

def processSeries(series, groupCrid, seriesTitleMap, xmlNS, allWrittenTitles, titleTuple, titleWriter):
        # we want to output series crid and title (tab seperated)

    seriesCrid = series.attrib.get('groupId')
    basicDesc = series.find(  "{%s}BasicDescription" % rootNS  )
    titles = basicDesc.findall("{%s}Title" % rootNS )
    for title in titles:
        writeTitle(title, seriesCrid, xmlNS, TitleDetails, allWrittenTitles, titleTuple, titleWriter)