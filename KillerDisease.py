#!/usr/bin/python

import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
import plotly 
import plotly.graph_objs as go


def parse(filename):

	deaths = pd.read_csv(filename)
	return deaths


def get_top10_killers(deaths, Sex='Persons', country_code='USA'):
	
	"""
	Returns data frame with top ten killer diseases
	for country with country_code
	Inputs :
	   deaths       ->  dataframe
	   Sex          -> 'Males', 'Females', 'Persons' (Persons is for male+female)
	   country_code -> Three letter country code
	"""

	data = deaths[ deaths['Sex'] == Sex ]
	data = data[['Disease Name', country_code]].set_index('Disease Name')
	data.sort_values(by=country_code, ascending=False, inplace=True)

	return data.loc[ data.index[0:9] ]


def make_figure(males, females, country_code='USA'):
	#https://plot.ly/python/pie-charts/
	fig = {
  	"data": [
    	{
		"values": list(males[country_code].values),
		"labels": list(males.index),
		"domain": {"x": [0, .48]},
		"name": "Deaths",
		"hoverinfo":"label+percent+name",
		"hole": .4,
		"type": "pie"
    	},
	{
      		"values": list(females[country_code].values),
      		"labels": list(females.index),
      		"text":["Female"],
      		"textposition":"inside",
		"domain": {"x": [.50, 1]},
		"name": "Deaths",
		"hoverinfo":"label+percent+name",
		"hole": .4,
		"type": "pie"
	}],

  	"layout": {
        	"title":"Cause of Deaths in "+country_code,
        	"annotations": [
            	{
                	"font": {
                    	"size": 20
                	},
                	"showarrow": False,
                	"text": "Males",
                	"x": 0.22,
                	"y": 0.5
            	},
            	{
                	"font": {
                    	"size": 20
                	},
                	"showarrow": False,
                	"text": "Females",
                	"x": 0.78,
                	"y": 0.5
            	}
        	]
    	}
	
	}

	return fig


if __name__=="__main__":

	filename = sys.argv[1]
	country_code = sys.argv[2]
	
	deaths = parse(filename)	

	males = get_top10_killers(deaths, 'Males', country_code)
	females = get_top10_killers(deaths, 'Females', country_code)
	
	fig = make_figure(males, females, country_code)

	plotly.offline.plot(fig, 
		filename = country_code+'_cause_of_death_2015.html',
		show_link=True,
		#output_type='div',
		auto_open=True
	)

	#print(plot)	



