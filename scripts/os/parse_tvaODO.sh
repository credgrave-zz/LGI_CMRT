###########################################################################
# Name: parse_tva.sh
# Author: Chris Redgrave
# Description: 	This script will parse the tva xml file and then push the
# 				resulting tsv file into the cmrt hdfs directories. This is
#				based on the audience measurement parse scripts.
#
#
# Version	Date 		Author				Description
###########################################################################
# 001		26/01/2016	C.Redgrave			1. Original Version
# 002		27/01/2016	C.Redgrave			1. Altered to collect TVA from BDA
###########################################################################

local_data=/home/bigdata/group/videorep/cmrt/data
hdfs_data=/user/group/videorep/data/cmrt
script_home=/home/bigdata/group/videorep/cmrt/scripts/python
tva_home=/user/group/videorep/audience_measurement/data/tva



cd $script_home

set -x
country=$1
process_date=$2

if [ -z "$2" ]
then
  process_date=$(date +%Y-%m-%d)
else
  process_date=$2
fi

echo "###################################################"
echo "# Gather and Parse TVA XML File"
echo "###################################################"
# Set variable to the xml file that has been previously extracted 
# by the Audience Measurement Project
hdfs_tva_file=$tva_home/${country}/TVA_${country}_${process_date}

#Grab TVA File from BDA and Put into CMRT Directory
hdfs dfs -copyToLocal ${hdfs_tva_file}.xml.zip $local_data

local_tva_file=$local_data/TVA_${country}_${process_date}

unzip -o ${local_tva_file}.xml.zip -d ${local_data}

echo "Processing File: ${tva_file}"
python parseTVA_CMRT_ODO.py ${local_data}/${country}/TVA_${country}_${process_date}.xml $local_data $country $process_date 

sftp cmrt@172.16.78.38 <<< "put $local_data/CMRT_content_onDemand_${country}_${process_date}.csv"


echo "Cleaning Up Files from the Data Directory"
rm -rf $local_data/*.csv

exit

