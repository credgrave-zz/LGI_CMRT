select system, language, keyword_bucket, count(distinct asset_crid)
from (
select 
    sys.source_system as system, ct.country_code, asset.asset_crid, asset.asset_title, f.language, 
    bc.conformed_broadcaster as broadcaster, ch.conformed_channel as channel, st.conformed_studio as studio,
    gen.conformed_genre as genre, subgen.conformed_genre as subgen, 
    --count(distinct f.asset_wid) asset_count,
    case 
      when (f.short_synopsis_word_count = f.long_synopsis_word_count) and (f.short_synopsis_word_count = f.medium_synopsis_word_count)
    then 'Y' else 'N' end as is_synopsis_the_same,
    case when keyword_count < 10 then '->'||to_char(keyword_count) else '10+' end keyword_bucket
from 
    fact_cmrt_availability f,
    dim_cmrt_age_rating rating,
    dim_cmrt_asset asset,
    dim_cmrt_broadcaster bc,
    dim_cmrt_channel ch,
    dim_cmrt_genre gen,
    dim_cmrt_genre subgen,
    dim_cmrt_studio st,
    dim_cmrt_system sys,
    dim_country ct,
    dim_date dt
where
    rating.object_wid = f.age_rating_wid
and asset.object_wid = f.asset_wid
and bc.object_wid = f.broadcaster_wid
and ch.object_wid = f.channel_wid
and gen.object_wid = f.genre_wid
and subgen.object_wid = f.subgenre_wid
and st.object_wid = f.studio_wid
and sys.object_wid = f.system_wid
and ct.object_wid = f.country_wid
and (f.meta_valid_for_start_date_time <= dt.time_id  and f.meta_valid_for_end_date_time > dt.time_id )
and dt.time_id = trunc(sysdate)
--and dt.calendar_month ;
)
group by 
system, language, keyword_bucket
order by 2,1;