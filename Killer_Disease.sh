#!/usr/bin/bash


while read -r aline; do
	
	echo ${aline} >tmp
	code=`awk '{print $1}' tmp`
	python Killer_Disease.py ${code}
	#echo ${code}
	
done<country_names.txt
