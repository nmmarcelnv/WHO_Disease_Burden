#!/usr/bin/python

import pandas as pd
import sys
import re

def get_country_names(filename):
	
	df = pd.read_excel(filename, sheetname=1, skiprows=6, nrows=2)
	cols = df.columns[7:len(df.columns)]
	df = df[cols]
	codes = df.iloc[0]
	out=open('country_names.csv','w')
	country_names = [name for name in df.columns] 
	for i in range(len(country_names)):
		name = country_names[i]
		pos = name.find("(")
		if pos != -1:
			name=name[0:pos]
		out.write(codes[i]+","+name+"\n")
		country_names[i]=name
	out.close()
	return codes, country_names

if __name__=="__main__":

	filename = sys.argv[1]
	codes, country_names = get_country_names(filename)
