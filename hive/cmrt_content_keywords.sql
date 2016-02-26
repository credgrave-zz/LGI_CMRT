CREATE EXTERNAL TABLE cmrt.cmrt_content_keywords
(
	crid					string
, 	language				string
, 	keyword 				string
, 	country 				string
,   process_date 			string
)
PARTITIONED BY (file_country string, file_process_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/cmrt_content_keywords/';
