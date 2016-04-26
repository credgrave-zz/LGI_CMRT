CREATE EXTERNAL TABLE cmrt.cmrt_reference
(
	classification	string
, 	language		string
, 	key				string
, 	value			string
, 	country 		string
, 	process_date 	string
)
PARTITIONED BY (file_country string, file_process_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/cmrt_reference/';

