CREATE EXTERNAL TABLE cmrt.cmrt_content_credits
(
	crid 				string
, 	language 			string
, 	given_name			string
, 	family_name			string
, 	presentation_role	string
, 	country 			string
, 	process_date 		string
)
PARTITIONED BY (file_country string, file_process_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/cmrt_content_credits/';
