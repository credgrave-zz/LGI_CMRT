CREATE EXTERNAL TABLE cmrt.cmrt_content_genre
(
	crid					string
, 	language				string
, 	genre_type				string
, 	genre_classification	string
, 	genre_code				string
, 	genre_value				string
, 	country 				string
,	process_date 			string
)
PARTITIONED BY (file_country string, file_process_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/cmrt_content_genre/';
