CREATE TABLE lnd_tva_program_info_title
(
  program_crid      string
, titleType       	string
, lang         		string
, titleText 		string   
)
PARTITIONED BY (country string, load_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/tva/PROGRAM_INFORMATION_TITLE/';



hive -e "use cmrt;alter table lnd_tva_program_info_title add partition(country='NL', load_date='2016-01-20');"
