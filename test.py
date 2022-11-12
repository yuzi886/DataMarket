import asyncio
 
import websockets

import json

import pandas as pd
import chardet 
import csv

#path = input("Enter a csv file address: ")
path = "csv/14-us-counties.csv"
df = pd.read_csv(path,encoding = 'ISO-8859-1')
data = df.to_json()
my_dict=json.loads(data)
for line in my_dict.items():
	#data_string = json.dumps(line[1])
	print(line[0])

"""with open("csv/_3-phe_vaccines_age_london_boroughs.csv", 'rb') as file:
	csvReader = csv.DictReader(file)
	for x in csvReader:
		print(x)
"""
"""df = pd.read_csv("csv/_3-phe_vaccines_age_london_boroughs.csv",encoding = 'ISO-8859-1')"""
#print(data)