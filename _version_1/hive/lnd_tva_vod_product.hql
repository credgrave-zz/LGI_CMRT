CREATE TABLE lnd_tva_vod_product
(
	groupCrid					string
,	title						string
,	shortSynopsis				string
,	mediumSynopsis				string
,	longSynopsis				string
,	UPCAgeRatingCS_2008			string
,	AgeCS_2010					string
,	SUBSCRIPTION_PACKAGE_ID		string
,	VodBackOfficeId				string
,	provider					string
,	vod_type					string
)
PARTITIONED BY (country string, load_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/tva/VOD_PRODUCT/';



hive -e "use cmrt;alter table lnd_tva_vod_product add partition(country='NL', load_date='2016-01-20');"



