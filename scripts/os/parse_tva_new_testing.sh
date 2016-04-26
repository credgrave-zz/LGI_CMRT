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
