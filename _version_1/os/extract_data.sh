###########################################################################
# Name: 
# Author: Chris Redgrave
# Description: 	
#
#
# Version	Date 		Author				Description
###########################################################################
# 001		26/01/2016	C.Redgrave			1. Original Version
#
###########################################################################

country=$1
load_date=$2

cmrt_output_dir=/home/bigdata/group/videorep/cmrt/cmrt_output


echo "*****************************"
echo "Starting Export for Country=${country} Process Date=${load_date}"
echo "*****************************"
echo "*****************************"
echo "Exporting dim_content_credits"
echo "*****************************"
hive -e "
INSERT OVERWRITE LOCAL DIRECTORY '${cmrt_output_dir}/dim_content_credits_${country}_${load_date}' 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\n' 
SELECT * FROM cmrt.perf_cmrt_dim_content_credits WHERE country='\"$country\"' AND load_date='\"$load_date\"';"

echo "*****************************"
echo "Exporting dim_content"
echo "*****************************"
hive -e "
INSERT OVERWRITE LOCAL DIRECTORY '${cmrt_output_dir}/dim_content_${country}_${load_date}' 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\n' 
SELECT * FROM cmrt.perf_cmrt_dim_content WHERE country='\"$country\"' AND load_date='\"$load_date\"';"

echo "*****************************"
echo "Exporting dim_content_certification"
echo "*****************************"
hive -e "
INSERT OVERWRITE LOCAL DIRECTORY '${cmrt_output_dir}/dim_content_certification_${country}_${load_date}' 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\n' 
SELECT * FROM cmrt.perf_cmrt_dim_content_certification WHERE country='\"$country\"' AND load_date='\"$load_date\"';"

echo "*****************************"
echo "Exporting dim_content_genre"
echo "*****************************"
hive -e "
INSERT OVERWRITE LOCAL DIRECTORY '${cmrt_output_dir}/dim_content_genre_${country}_${load_date}' 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\n' 
SELECT * FROM cmrt.perf_cmrt_dim_content_genre WHERE country='\"$country\"' AND load_date='\"$load_date\"';"

echo "*****************************"
echo "Exporting dim_content_keywords"
echo "*****************************"

hive -e "
INSERT OVERWRITE LOCAL DIRECTORY '${cmrt_output_dir}/dim_content_keywords_${country}_${load_date}' 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\n' 
SELECT * FROM cmrt.perf_cmrt_dim_content_keywords WHERE country='\"$country\"' AND load_date='\"$load_date\"';"

echo "*****************************"
echo "Exporting dim_content_synopsis"
echo "*****************************"
hive -e "
INSERT OVERWRITE LOCAL DIRECTORY '${cmrt_output_dir}/dim_content_synopsis_${country}_${load_date}' 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\n' 
SELECT * FROM cmrt.perf_cmrt_dim_content_synopsis WHERE country='\"$country\"' AND load_date='\"$load_date\"';"

echo "*****************************"
echo "Exporting fact_availability"
echo "*****************************"
hive -e "
INSERT OVERWRITE LOCAL DIRECTORY '${cmrt_output_dir}/fact_availability_${country}_${load_date}' 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '|' 
LINES TERMINATED BY '\n' 
SELECT * FROM cmrt.perf_cmrt_fact_availability WHERE country='\"$country\"' AND load_date='\"$load_date\"';"

echo "*****************************"
echo "Export Complete"
echo "*****************************"

echo "*****************************"
echo "Moving and Renaming Files"
echo "*****************************"
	
mv ${cmrt_output_dir}/dim_content_credits_${country}_${load_date}/000000_0 ${cmrt_output_dir}/dim_content_credits_${country}_${load_date}.csv
mv ${cmrt_output_dir}/dim_content_${country}_${load_date}/000000_0 ${cmrt_output_dir}/dim_content_${country}_${load_date}.csv
mv ${cmrt_output_dir}/dim_content_certification_${country}_${load_date}/000000_0 ${cmrt_output_dir}/dim_content_certification_${country}_${load_date}.csv
mv ${cmrt_output_dir}/dim_content_genre_${country}_${load_date}/000000_0 ${cmrt_output_dir}/dim_content_genre_${country}_${load_date}.csv
mv ${cmrt_output_dir}/dim_content_keywords_${country}_${load_date}/000000_0 ${cmrt_output_dir}/dim_content_keywords_${country}_${load_date}.csv
mv ${cmrt_output_dir}/dim_content_synopsis_${country}_${load_date}/000000_0 ${cmrt_output_dir}/dim_content_synopsis_${country}_${load_date}.csv
mv ${cmrt_output_dir}/fact_availability_${country}_${load_date}/000000_0 ${cmrt_output_dir}/fact_availability_${country}_${load_date}.csv

echo "*****************************"
echo "Removing redundant directories"
echo "*****************************"
rm -rf ${cmrt_output_dir}/dim_content_credits_${country}_${load_date}
rm -rf ${cmrt_output_dir}/dim_content_${country}_${load_date}/
rm -rf ${cmrt_output_dir}/dim_content_certification_${country}_${load_date}
rm -rf ${cmrt_output_dir}/dim_content_genre_${country}_${load_date}
rm -rf ${cmrt_output_dir}/dim_content_keywords_${country}_${load_date}
rm -rf ${cmrt_output_dir}/dim_content_synopsis_${country}_${load_date}
rm -rf ${cmrt_output_dir}/fact_availability_${country}_${load_date}/

exit;
