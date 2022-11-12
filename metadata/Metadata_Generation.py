import pandas as pd
import json
import sys
from Mysql import Select_column,Insert_Row
import csv
def File_size(dataset):
	return sys.getsizeof(dataset)


def Record_Num(dataset):
	return len(dataset)

def Column_Num(dataset):
	return len(dataset["0"])

def Process(ID):
	#print(Insert_Row("Dataset",["user_id","host_link"],["1","'/home/csimage/git/DataMarket/csv/industry.csv'"]))

	condition = "id = {Id}".format(Id = ID)
	path = Select_column("host_link","Dataset",condition)
	df = pd.read_csv(path[0][0],encoding = 'ISO-8859-1')
	data = df.to_json(orient='index')
	my_dict=json.loads(data)
	file_size = File_size(my_dict)
	record_num = Record_Num(my_dict)
	column_num = Column_Num(my_dict)

	

Process(2)