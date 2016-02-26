set -x
country=$1
process_date=$2

if [ -z "$2" ]
then
  process_date=$(date +%Y-%m-%d)
else
  process_date=$2
fi


#Filesystem Variables
SFTP_DIR=/
JSON_INPUT_DIR=/home/cloudera/_work/_LGI/json_input
SCRIPT_DIR=/home/cloudera/_work/_LGI/python
PROCESS_DATE=$(date +%Y%m%d)

#HDFS Variables
HDFS_DATA_DIR=/user/cloudera/crmt_json

for file in /home/cloudera/_work/_LGI/json_input/*
do
	file="${file%.*}"
	file_country=`basename $file`
	file_country="${file_country:0:2}"

	echo "Parsing JSON file into TSV"
	python $SCRIPT_DIR/parse_ditto_json.py $file.json $file.tsv NL $PROCESS_DATE


	echo "Creating new HDSF partition"
	hdfs dfs -mkdir $HDFS_DATA_DIR/$PROCESS_DATE/
	hdfs dfs -mkdir $HDFS_DATA_DIR/$PROCESS_DATE/$file_country/

	echo "Adding TSV file into HDFS"
	hdfs dfs -put $file.tsv $HDFS_DATA_DIR/$file_country/$PROCESS_DATE/

	#Change for Json File
	#hdfs dfs -copyFromLocal -f $local_data/PROGRAM_INFORMATION/${country}/${process_date}/titles/${country}titles${process_date}.tsv $hdfs_data/PROGRAM_INFORMATION_TITLES/country=${country}/load_date=${process_date}
	#hive -e "use audience_measurement;alter table PROGRAM_INFORMATION_TITLES add partition(country='"${country}"', load_date='"${process_date}"');"
	#if `hdfs dfs -test -e $hdfs_data/PROGRAM_INFORMATION/country=${country}/load_date=${process_date}/${country}content${process_date}.tsv`
	#then
	#	rm $local_data/PROGRAM_INFORMATION/${country}/${process_date}/${country}content${process_date}.tsv
	#	rm  $local_data/PROGRAM_INFORMATION/${country}/${process_date}/titles/${country}titles${process_date}.tsv
	#fi

done

exit