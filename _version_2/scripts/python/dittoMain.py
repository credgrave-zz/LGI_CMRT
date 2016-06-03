# This Python file uses the following encoding: utf-8

# Standard Module Imports
import os
import sys
import re

# Custom Module Imports
import dittoAvailability

#Arguments
infile_json= sys.argv[1]
outfile_path= sys.argv[2]
ditto_country= sys.argv[3]
ditto_date= sys.argv[4]


# check input file
#if not os.path.exists(infile_json):
#    print 'input file', infile_json, 'does not exist'
#    sys.exit(-1)

# XML Constants
dittoAvailability.parseWriteDittoAvailability(infile_json, outfile_path, ditto_country, ditto_date)



