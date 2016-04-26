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
	echo "# Getting Ditto file from hdfs"
	echo "###################################################"
hdfs dfs -copyToLocal ${hdfs_data}/cmrt_ditto_content_availability/file_country=${country}/file_process_date=${process_date}/CMRT_ditto_content_availability_${country}_${process_date}.csv $local_data




echo "###################################################"
echo "# Pushing Data Files to Informatica"
echo "###################################################"

echo "Compressing Files"
zip $local_data/CMRT_${country}_${process_date}.zip $local_data/*.csv
echo "Creating Trigger File"
touch $local_data/CMRT.${country}.completed
echo "Transferring Data to FTP Server"

sftp cmrt@172.16.78.38 <<< "put $local_data/CMRT_${country}_${process_date}.zip"


echo "Cleaning Up Files from the Data Directory"
rm -rf $local_data/*.csv
rm -rf $local_data/${country}
rm -rf $local_data/*.json
rm -rf $local_data/CMRT.${country}.completed
rm -rf $local_data/*.csv.zip


exit

