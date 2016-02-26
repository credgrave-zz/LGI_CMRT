  CREATE OR REPLACE VIEW perf_cmrt_dim_content_synopsis
AS
  SELECT concat('"',on_demand.programcrid,'"') AS programcrid
  ,     concat('"',product.groupcrid,'"') AS crid
  , 		concat('"',product.shortsynopsis,'"') AS shortsynopsis
  ,     concat('"',product.mediumsynopsis,'"') AS mediumsynopsis
  ,     concat('"',product.longsynopsis,'"') AS longsynopsis
  ,     concat('"',product.country,'"') AS country
  ,     concat('"',product.load_date,'"') AS load_date
  FROM lnd_tva_vod_product product
  ,    lnd_tva_on_demand_program on_demand
  WHERE product.groupcrid = on_demand.productid ;

CREATE OR REPLACE VIEW perf_cmrt_dim_content
AS
  SELECT  concat('"',program_crid,'"') AS crid
  ,     concat('"',lang,'"') AS language
  ,     concat('"',titletext,'"') AS title
  ,     concat('"',country,'"') AS country
  ,     concat('"',load_date,'"') AS load_date
  FROM lnd_tva_program_info_title;  

CREATE OR REPLACE VIEW perf_cmrt_dim_content_genre
AS
  SELECT 	concat('"',program_crid,'"') AS crid
  ,     concat('"',series_crid,'"') AS series_crid
  ,     concat('"',maingenre,'"') AS maingenre
  ,     concat('"','subGenre','"') AS subGenre
  ,     concat('"',country,'"') AS country
  ,     concat('"',load_date,'"') AS load_date
    FROM lnd_tva_program_info_content; 


CREATE OR REPLACE VIEW perf_cmrt_dim_content_keywords
AS
  SELECT 	concat('"',program_crid,'"') AS crid
  ,     concat('"',series_crid,'"') AS series_crid
  ,     concat('"','lang','"') AS lang
  ,     concat('"',myKeywords,'"') AS myKeywords
  ,     concat('"',country,'"') AS country
  ,     concat('"',load_date,'"') AS load_date
    FROM lnd_tva_program_info_content
    LATERAL VIEW explode(keywords) tst AS myKeywords;


CREATE OR REPLACE VIEW perf_cmrt_dim_content_certification
AS
  SELECT concat('"',on_demand.programcrid,'"') AS programcrid
  ,     concat('"',product.groupcrid,'"') AS groupcrid
  ,     concat('"','lang','"') AS lang
  ,     concat('"',product.upcageratingcs_2008,'"') AS upcageratingcs_2008
  ,     concat('"',product.agecs_2010,'"') AS agecs_2010
  ,     concat('"',product.country,'"') AS country
  ,     concat('"',product.load_date,'"') AS load_date
    FROM lnd_tva_vod_product product
    ,    lnd_tva_on_demand_program on_demand
    WHERE product.groupcrid = on_demand.productid 

CREATE OR REPLACE VIEW perf_cmrt_fact_availability
AS
	SELECT concat('"',systemname,'"') AS systemname
  ,     concat('"',crid,'"') AS crid
  ,     concat('"',request,'"') AS request
  ,     concat('"',requesttime,'"') AS requesttime
  ,     concat('"',exist,'"') AS exist
  ,     concat('"',exists,'"') AS exists
  ,     concat('"',availabilitytime,'"') AS availabilitytime
  ,     concat('"',state,'"') AS state
  ,     concat('"',country,'"') AS country
  ,     concat('"',load_date,'"') AS load_date
  	FROM lnd_tva_lnd_json_ditto; 

CREATE OR REPLACE VIEW perf_cmrt_dim_content_credits
AS
  SELECT 	concat('"',program_crid,'"') AS crid
  ,     concat('"',series_crid,'"') AS series_crid
  ,     concat('"','lang','"') AS lang
  ,     concat('"',myCastList,'"') AS myCastList
  ,     concat('"',country,'"') AS country
  ,     concat('"',load_date,'"') AS load_date
    FROM lnd_tva_program_info_content 
    LATERAL VIEW explode(castlist) tst AS myCastList;	