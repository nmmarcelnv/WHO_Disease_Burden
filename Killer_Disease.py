import numpy as np
import pandas as pd
from tabulate import tabulate
import sys 
import matplotlib.pyplot as plt
import seaborn
import os 

"""data source: http://www.who.int/healthinfo/global_burden_disease/estimates/en/index2.html"""
alphabet = ['A.', 'B.', 'C.', 'D.', 'F.', 'G.', 'H.', 'I.', 'J.', 'K.', 'L.', 'M.', 'O.', 'P.'] 

def get_death_data():
	"""Get death data from WHO website."""
	success = 0
	if os.path.exists('GHE2015_Deaths-2000-country.xls'):
		print("-- GHE2015_Deaths-2000-country.xls found locally")
		success = 1
	else:
		print("-- trying to download GHE2015_Deaths-2000-country.xls from from the WHO website")
		fn = ("http://www.who.int/entity/healthinfo/global_burden_disease/" +
			"GHE2015_Deaths-2000-country.xls")
		print(fn)
		try:
			command="wget "+fn
			os.system(command)

			if os.path.exists('GHE2015_Deaths-2000-country.xls'):
				print("..successfully downloaded GHE2015_Deaths-2000-country.xls")
				success = 1
		except:
			exit("-- Unable to download GHE2015_Deaths-2000-country.xls")

	return success

def parse(country_code):
	"""parse the excel file, remove unnecessary headers and define names for first 7 columns
	Note that the remaining columns are the country names/code
	
	Input:  file name = "GHE2015_Deaths-2000-country.xls"
		country code : The country we want to see top ten killer disease. eg. VEN for Venezuala
	"""	
	success = get_death_data()
	filename = "GHE2015_Deaths-2000-country.xls"
	names = ['sex', 'GHEcode', 'Disease Category', 'GHEcause', 'group', 'Disease Name', 'dclass']

	df = pd.read_excel(filename, sheet_name=1, skiprows=7)
	n = names.copy() 

	for col in df.columns[7:]:
		n.append(col)
		#print(col)
	df.columns = n
	names.append(country_code)

	return df[names]


def Isalpha(s):

	ans = False
	if type(s) != str:
		return ans

	if (len(s) == 2) and ('.' in s)  and s[0].isalpha():
		ans = True
	return ans

	
def clean_GHEcause(df):
	"""Do some cleaning on the columns named GHEcause
	Basically drop irrelevant rows used as names"""

	indices = df.index
	i = indices[0]
	subs = df.ix[i, 'group']
	to_drop = [] 
	for n in range(len(indices)):
		i = indices[n]	
		if ( Isalpha(df.ix[i, 'GHEcause']) ) :
			subs = df.ix[i, 'group']
			to_drop.append(i)
		df.ix[i, 'GHEcause'] = subs
	df.drop(to_drop, axis=0, inplace=True) 


def clean_dname(df):
	"""Do some cleaning on the columns named dname
	Basically drop irrelevant rows used as names"""

	indices = df.index
	df['Dname'] = df['Disease Name'].apply(Isalpha)
	allAs = df['Disease Name']=='a.'
	ind = allAs[allAs==True].index

	to_drop = ind-1
	for n in range(len(indices)):
		i = indices[n]
		if ( Isalpha(df.ix[i, 'Disease Name']) ) :
			df.ix[i, 'Disease Name'] = df.ix[i, 'dclass']	
				
	df.drop(to_drop, axis=0, inplace=True)	
	df.drop(['group', 'dclass', 'Dname'], axis=1, inplace=True)	


def clean_cathegory(df):
	"""The WHO health outcomes are grouped into 3 main categories: 
	I  = Communicable Diseases 
	II = Non Communicable Diseases 
	III= Injuries """

	#get the row index for each of the categories
	I   = df[ df['Disease Category']=='I.' ].index[0]
	II  = df[ df['Disease Category']=='II.' ].index[0]
	III = df[ df['Disease Category']=='III.' ].index[0]

	#Fill up empty space in data frame with category name
	df.ix[0:II-1, 'Disease Category'] = 'Communicable'
	df.ix[II:III-1, 'Disease Category'] = 'NCommunicable'
	df.ix[III:, 'Disease Category'] = 'Injuries'
	
	#drop these rows, since they only contain summary for each category
	df.drop([I,II,III], axis=0, inplace=True)


def write_csv(df):

	df.drop(df.index[0:2], axis=0, inplace=True)
	
	#do some cleaning
	clean_cathegory(df)
	clean_GHEcause(df)
	clean_dname(df)
	
	#missing values are recorded as '.', replace with NA
	df.replace('.', 'NaN', inplace=True)

	df.to_csv('GHE2015_Deaths_2000_country.csv', index=False)


def clean(df, country_code):
	d = {}
	
	#first group the data frame by sex
	df_groups = df.groupby('sex')

	for key in df_groups.groups.keys():
		df_key = df_groups.get_group(key).copy()

		#The two first row of each subgroup are irrelevant, drop them
		df_key.drop(df_key.index[0:2], axis=0, inplace=True)

		#do some cleaning
		clean_cathegory(df_key)
		clean_GHEcause(df_key)
		clean_dname(df_key)

		#missing values are recorded as '.', replace with 0
		df_key.replace('.', 0, inplace=True)

		#sort to get top ten
		df_key.sort_values(country_code, ascending=False, inplace=True) 
		Top10Killer = df_key.index[0:10]
		#d[key] = df_key.ix[Top10Killer, ['Disease Category', 'Disease Name', country_code]] 
		d[key] = df_key.ix[Top10Killer, :]
	return d


def get_country_names(filename):
	
	df = pd.read_excel(filename, sheet_name=1, skiprows=6, nrows=2)
	cols = df.columns[7:len(df.columns)-1]
	df = df[cols]
	codes = df.iloc[0]
	out=open('country_names.txt','w')
	country_names = [name for name in df.columns] 
	for i in range(len(country_names)):
		name = country_names[i]
		pos = name.find("(")
		if pos != -1:
			name=name[0:pos]
		out.write(codes[i]+" "+name+"\n")
		country_names[i]=name
	out.close()
	dic={codes[i]:country_names[i] for i in range(len(codes))}
	return dic
"""
def Print(df):
	print ( tabulate(df, headers='keys', tablefmt='psql') )
	return
"""

if __name__=="__main__":
	
	country_code = sys.argv[1] 
	df  = parse(country_code)
	dic = clean(df, country_code)
	df_male   = dic['Males']
	df_female = dic['Females']

	#write_csv(df)

	countries=get_country_names('GHE2015_Deaths-2000-country.xls')
	#create a color map RGB, each tuple will be used for a bar	
	customcmp = [(i/10.0, i/40.0, 0.05) for i in range(len(dic['Males']))]

	#create title for the plot
	title='Top 10 Killer Diseases among males and females in '+countries[country_code]

	#create subplots for to plot data for males and females
	fig, (axMale, axFemale)	= plt.subplots(2,1, figsize=(10,8))

	#set the disease name as the index, since df[coln].plot() uses the index a labels by default	
	df_male.set_index('Disease Name', drop=True, inplace=True)
	df_female.set_index('Disease Name', drop=True, inplace=True)

	#create a bar chart of the column called country_code. This column has the number of deaths
	df_male[country_code].plot(	kind='barh',  	#horizontal bar chart
					ax=axMale, 	#plot on the axMale axes
					color=customcmp,#each bar has its own color 
					alpha=0.6, 	#transparency
					label='Males')

	df_female[country_code].plot(	kind='barh', 
					ax=axFemale, 
					color=customcmp, 
					alpha=0.6, 
					sharex=axMale,
					label='Females') 

	axFemale.set_xticks([])
	axFemale.set_xlabel('Death Rate ---->')
	
	#remove default y label
	axFemale.set_ylabel('')

	#use seaborn to turn of left, top and right frame lines
	#axFemale.spines["right"].set_visible(False)
	seaborn.despine(left=True, top=True, right=True)

	axMale.set_title(title, fontsize = 14.0) 

	#write a text on figure. By default, position x, y are based on the data 
	axFemale.text(  x= 0.80, y =0.80, s = 'Female',
                        transform=axFemale.transAxes, #change coordinate to plot scale
                        fontsize = 14,
                        color = 'blue' )
	

	axMale.set_ylabel('')
	axMale.text(	x= 0.80, y =0.80, s = 'Male', 
			transform=axMale.transAxes,
			fontsize = 14,
			color = 'blue' 
		   )

	fig.tight_layout()
	plt.savefig(country_code+'.png')
	#plt.show()
