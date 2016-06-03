###########################################################################
# Name: getHistoricTVA.sh
# Author: Chris Redgrave
# Description: 	This script will get the processed tva data from the bda
#
#
# Version	Date 		Author				Description
###########################################################################
# 001		18/04/2016	C.Redgrave			1. Original Version
###########################################################################

local_data=/home/bigdata/group/videorep/cmrt/data
hdfs_data=${hdfs_data}
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

hdfs dfs -copyToLocal ${hdfs_data}/cmrt_content/file_country=${country}/file_process_date=${process_date}/CMRT_content_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_content_certification/file_country=${country}/file_process_date=${process_date}/CMRT_content_certification_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_content_credits/file_country=${country}/file_process_date=${process_date}/CMRT_content_credits_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_content_distributer/file_country=${country}/file_process_date=${process_date}/CMRT_content_distributer_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_content_genre/file_country=${country}/file_process_date=${process_date}/CMRT_content_genre_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_content_keywords/file_country=${country}/file_process_date=${process_date}/CMRT_content_keyword_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_content_synopsis/file_country=${country}/file_process_date=${process_date}/CMRT_content_synopsis_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_ditto_content_availability/file_country=${country}/file_process_date=${process_date}/CMRT_ditto_content_availability_${country}_${process_date}.csv $local_data
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_reference/file_country=${country}/file_process_date=${process_date}/CMRT_reference_${country}_${process_date}.csv $local_data

zip $local_data/CMRT_${country}_${process_date}.zip $local_data/*.csv

sftp cmrt@172.16.78.38 <<< "put $local_data/CMRT_${country}_${process_date}.zip"