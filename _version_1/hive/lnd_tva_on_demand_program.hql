CREATE TABLE lnd_tva_on_demand_program
(
   VodBackOfficeId string
  ,productId	string
  ,programCrid	string
  ,contentProvider	string
  ,contentProviderId	string
  ,publishedStartTime string	
  ,publishedEndTime	string
  ,publishedDuration string	
  ,NetworkId	string
  ,TransponderId string
  ,ServiceId string
)
PARTITIONED BY (country string, load_date string) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/group/videorep/data/cmrt/tva/ON_DEMAND_PROGRAM/';



hive -e "use cmrt;alter table lnd_tva_on_demand_program add partition(country='NL', load_date='2016-01-20');"

