CREATE TABLE lnd_tva_program_info_content
(
  program_crid      string
, series_crid       string
, mainGenre         string
, durationInSeconds string   
, EpisodeNumber     string
, HasPreview        string
, IsPreviewOf       string
, keyWords          array<string>
)
PARTITIONED BY (country string, load_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/tva/PROGRAM_INFORMATION/';



hive -e "use cmrt;alter table lnd_tva_program_info_content add partition(country='NL', load_date='2016-01-20');"