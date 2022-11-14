import pandas as pd
import json
import sys
from Mysql import Select_column,Insert_Row
import csv
import numpy as np


def File_size(dataset):
	return sys.getsizeof(dataset)

def Record_Num(dataset):
	return len(dataset)

def Column_Num(dataset):
	return len(dataset)

def Column_name(dataset):
	return dataset[0]

def Data_type(dataset):
	return type(dataset[1]["0"]).__name__

def Missing_value(dataset):
	df1 = pd.DataFrame(list(dataset[1].values()),columns = [dataset[0]])
	#list(dataset[1].values())
	return df1.isnull().sum().sum()

def Unique_value(dataset):
	res = np.array(list(dataset[1].values()))
	unique_res = np.unique(res)
	return unique_res.size

def Max_num(dataset):
	return max(list(dataset[1].values()))

def Min_num(dataset):
	return min(list(dataset[1].values()))

def Store_database(value_list):# store the metadata in database
	column_name = "dataset_id,total_records,total_columns,file_size,summary"
	result = Insert_Row("Quality_information_Metadata", column_name,value_list)
	if result == True:
		print("Data store in Quality_Information_Metadata table successfully")
	else:
		print("Data don't store in Quality_Information_Metadata table ")

def Process(ID):#id is the file id in the database 

	condition = "id = {Id}".format(Id = ID)
	path = Select_column("host_link","Dataset",condition)
	df = pd.read_csv(path[0][0],encoding = 'ISO-8859-1')
	data = df.to_json()
	my_dict=json.loads(data)
	file_size = File_size(my_dict)
	column_num = Column_Num(my_dict)
	record_num = Record_Num(my_dict[list(my_dict)[0]])

	#the metadata for every column 
	field = ["column_name","data_type","missing_value_num","unique_value_num","max_value","min_value"]
	rows =[]
	for column in my_dict.items():
		column_name = Column_name(column)
		data_type = Data_type(column)
		#value = list(dataset[1].values())
		missing_value = Missing_value(column)
		unique_value = Unique_value(column)
		if data_type in ['int','float','long','complex']:
			max_num = Max_num(column)
			min_num = Min_num(column)
		else:
			max_num = None 
			min_num = None
		row = [column_name,data_type,missing_value,unique_value,max_num,min_num]
		rows.append(row)

	#turn the information to its specific file
	ori_path = path[0][0].split(".")
	output_path = ori_path[0] +"_"+column_name+".csv"
	with open(output_path, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow(field)
		csvwriter.writerows(rows)
	Store_database([ID,record_num,column_num,file_size,output_path])
	return output_path




Process(4)
