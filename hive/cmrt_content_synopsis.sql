CREATE EXTERNAL TABLE cmrt.cmrt_content_synopsis
(
	crid			string
, 	language 		string
, 	synopsis_type	string
, 	synopsis  		string
, 	country 		string
, 	process_date 	string
)
PARTITIONED BY (file_country string, file_process_date string) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\f'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/cmrt_content_synopsis/';
