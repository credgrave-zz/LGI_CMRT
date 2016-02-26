CREATE EXTERNAL TABLE cmrt.cmrt_ditto_content_availability
(
	systemname 			string
, 	crid 				string
, 	request 			string
, 	requesttime 		string
, 	exist 				string
, 	exists_ 			string
, 	availabilitytime 	string
, 	state 				string
, 	ditto_country 		string
, 	ditto_date 			string
)
PARTITIONED BY (file_country string, file_process_date string) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/cmrt_ditto_content_availability/';

