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
	python parseTVA_CMRT.py ${local_data}/${country}/TVA_${country}_${process_date}.xml $local_data $country $process_date 

	pythonRet=$?
	if [  $pythonRet -ne 0 ]; then
	    echo TVA Python failed $pythonRet
	    exit
	fi

	echo "###################################################"
	echo "# Retrieve JSON File from JSON File"
	echo "###################################################"

	json_process_date="$(echo ${process_date} | sed 's/-/_/g')"

	echo "JSON PROCESS DATE = ${json_process_date}"

	wget http://nl-ditto.chello.com/${country}_ditto_${json_process_date}.json -P $local_data



	echo "###################################################"
	echo "# Processing File: ${ditto_file}"
	echo "###################################################"
	ditto_file="${local_data}/${country}_ditto_${json_process_date}.json"

	python parse_ditto_json.py $ditto_file $local_data $country $process_date

	pythonRet=$?
	if [  $pythonRet -ne 0 ]; then
	    echo DITTO Python failed $pythonRet
	    exit
	fi


echo "###################################################"
echo "# Pushing Reference Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_reference/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_reference/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_reference_${country}_${process_date}.csv $hdfs_data/cmrt_reference/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_reference"
hive -e "use cmrt;alter table cmrt_reference add partition(file_country='"${country}"', file_process_date='"${process_date}"');"

echo "###################################################"
echo "# Pushing Certification Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_certification/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_certification/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_content_certification_${country}_${process_date}.csv $hdfs_data/cmrt_content_certification/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_content_certification"
hive -e "use cmrt;alter table cmrt_content_certification add partition(file_country='"${country}"', file_process_date='"${process_date}"');"



echo "###################################################"
echo "# Pushing Credits Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_credits/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_credits/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_content_credits_${country}_${process_date}.csv $hdfs_data/cmrt_content_credits/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_content_credits"
hive -e "use cmrt;alter table cmrt_content_credits add partition(file_country='"${country}"', file_process_date='"${process_date}"');"



echo "###################################################"
echo "# Pushing Distributer Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_distributer/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_distributer/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_content_distributer_${country}_${process_date}.csv $hdfs_data/cmrt_content_distributer/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_content_distributer"
hive -e "use cmrt;alter table cmrt_content_distributer add partition(file_country='"${country}"', file_process_date='"${process_date}"');"



echo "###################################################"
echo "# Pushing Genre Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_genre/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_genre/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_content_genre_${country}_${process_date}.csv $hdfs_data/cmrt_content_genre/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_content_genre"
hive -e "use cmrt;alter table cmrt_content_genre add partition(file_country='"${country}"', file_process_date='"${process_date}"');"


echo "###################################################"
echo "# Pushing Keyword Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_keywords/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_keywords/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_content_keywords_${country}_${process_date}.csv $hdfs_data/cmrt_content_keywords/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_content_keywords"
hive -e "use cmrt;alter table cmrt_content_keywords add partition(file_country='"${country}"', file_process_date='"${process_date}"');"


echo "###################################################"
echo "# Pushing Content Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_content/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_content/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_content_${country}_${process_date}.csv $hdfs_data/cmrt_content/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_content_keywords"
hive -e "use cmrt;alter table cmrt_content add partition(file_country='"${country}"', file_process_date='"${process_date}"');"


echo "###################################################"
echo "# Pushing Synopsis Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_synopsis/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_content_synopsis/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_content_synopsis_${country}_${process_date}.csv $hdfs_data/cmrt_content_synopsis/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_content_synopsis"
hive -e "use cmrt;alter table cmrt_content_synopsis add partition(file_country='"${country}"', file_process_date='"${process_date}"');"

echo "###################################################"
echo "# Pushing Availability Data to HDFS"
echo "###################################################"
hdfs dfs -mkdir -p $hdfs_data/cmrt_ditto_content_availability/file_country=${country}
hdfs dfs -mkdir -p $hdfs_data/cmrt_ditto_content_availability/file_country=${country}/file_process_date=${process_date}

hdfs dfs -copyFromLocal -f $local_data/CMRT_ditto_content_availability_${country}_${process_date}.csv $hdfs_data/cmrt_ditto_content_availability/file_country=${country}/file_process_date=${process_date}

echo "Adding Partitions to the HIVE Table: cmrt_ditto_content_availability"
hive -e "use cmrt;alter table cmrt_ditto_content_availability add partition(file_country='"${country}"', file_process_date='"${process_date}"');"



echo "###################################################"
echo "# Pushing Data Files to Informatica"
echo "###################################################"

echo "Compressing Files"
zip $local_data/CMRT_${country}_${process_date}.zip $local_data/*.csv
echo "Creating Trigger File"
touch $local_data/CMRT.${country}.completed
echo "Transferring Data to FTP Server"

#sftp user@hostname:$local_data/CMRT_${country}_${process_date}.zip
#sftp user@hostname:$local_data/CMRT.${country}.completed

echo "Cleaning Up Files from the Data Directory"
rm -rf $local_data/*.csv 
rm -rf $local_data/${country}
rm -rf $local_data/*.json
#rm -rf $local_data/CMRT.${country}.completed
rm -rf *.csv.zip

exit

