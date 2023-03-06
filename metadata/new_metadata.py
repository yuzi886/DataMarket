import pandas as pd
import json
import sys
from Mysql import Select_column,Insert_Row
import csv
import numpy as np
import mysql.connector
import re
"""
# sentence is the string that need to turn to regular expression
# return: regular expression according to the sentence 

"""

def turn_reg(sentence):
	split_list = list(sentence)
	last_type = ""
	regex_pattern = r''
	for i in range(len(split_list)):
		if split_list[i].isdigit():
			if last_type != "digit":
				regex_pattern += r'\d*'

			last_type = "digit"
		elif split_list[i].isalpha():
			if last_type != "alpha":
				regex_pattern += r'[a-zA-Z]*'
			last_type = "alpha"
		else:
			if last_type == "alpha" and split_list[i] == ' ':
				continue
			regex_pattern += re.escape(split_list[i])
			last_type = "special"

	"""elif split_list[i].isalpha() and split_list[i].islower():
							
										if last_type != "lower":
											regex_pattern += r'[a-z]*'
										last_type = "lower"
							
									elif split_list[i].isalpha() and split_list[i].isupper():
							
										if last_type != "upper":
											regex_pattern += r'[A-Z]*'
										last_type = "upper"""
	return regex_pattern

"""
# check how much cell in the column has the same format
# column: the list of column
# return: the number of cell which has the same format

max number of cell which has the same format / total number of cell in the column
"""
def consistent_num(column):
	"""	col_detail = (data.column_summary)[col] 
	if col_detail[5] == "str":
		df = pd.read_csv(data.host_link,encoding = 'ISO-8859-1')
		column = df[col].tolist()"""
	match_dict = {}
	for cell in column:
		if type(cell) == int or type(cell) == float:
			regex_pattern = r'^[+-]?\d*[.]?\d*$'
		else:
			regex_pattern = turn_reg(cell)
		if regex_pattern in match_dict:
			match_dict[regex_pattern] +=1
		else:
			match_dict[regex_pattern] = 1
	print(match_dict)
	return (max(match_dict.items(), key=lambda x:x[1]))[1]
	"""	else:"""
		#return data.total_records

def update(table_name,column_name,new_value,condition):
	"""UPDATE your_table SET your_column = 'new_value' WHERE primary_key = 1;"""
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		password="Kilburn",
		database="data_marketplace"
	)
	mycursor = mydb.cursor()
	flag = True
	try:
		query = "UPDATE %s SET %s=%s WHERE %s;"%(table_name,column_name,new_value,condition)
		print(query)
		mycursor.execute(query)
		mydb.commit()
	except Exception as e:
		flag = False
		print(e)
	finally:
		mydb.close()
		mycursor.close()
		return flag
	#return myresult

def column(table_name,column_name):
	"""SELECT whole column from Table"""
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		password="Kilburn",
		database="data_marketplace"
	)
	mycursor = mydb.cursor()
	mycursor.execute("SELECT %s FROM %s"%(column_name,table_name))
	myresult = mycursor.fetchall()
	mycursor.close()
	mydb.close()
	return myresult

def update_unique(ID):
	condition = "id = {Id}".format(Id = ID)
	path = Select_column("host_link","users_dataset",condition)
	df = pd.read_csv(path[0][0],encoding = 'ISO-8859-1')
	num_unique_rows = len(df.drop_duplicates())
	print(num_unique_rows)
	update("users_dataset","unique_num",str(num_unique_rows),"id ="+str(ID))
	

	"""df = pd.read_csv(path[0][0],encoding = 'ISO-8859-1')
				data = df.to_json()
				my_dict=json.loads(data)"""
def update_consistency(ID):
	condition = "id = {Id}".format(Id = ID)
	path = Select_column("host_link","users_dataset",condition)
	df = pd.read_csv(path[0][0],encoding='utf-8')
	column_summary = Select_column("column_summary","users_dataset", "id ="+str(ID))
	row_num = Select_column("total_records","users_dataset", "id ="+str(ID))
	summary = eval((column_summary[0][0]).replace('null', 'None'))
	column_names = df.columns.tolist()

	# Print the column names to check for errors
	print(column_names)
	for col, summ in summary.items():
		summ = summ[:7]
		if summ[5] == 'str':
			summ.append(consistent_num(df[col].tolist()))
		else:
			summ.append(row_num[0][0])
		summary[col] = summ
	summary = str(summary).replace('None','null')
	summary = summary.replace("'",'"')
	summary = "'"+summary+"'"
	update("users_dataset","column_summary",summary,"id ="+str(ID))

#update_consistency(4)
"""for item in column("users_dataset","id"):
	print(item[0])
	update_consistency(item[0])"""

"""ID = 16
condition = "id = {Id}".format(Id = ID)
path = Select_column("host_link","users_dataset",condition)"""

#df = pd.read_csv(path[0][0],encoding = 'utf-8')
#df = pd.read_csv('/home/csimage/git/DataMarket/data/4-phe_healthcare_admissions_age.csv',encoding = 'utf-8')
#column_summary = Select_column("column_summary","users_dataset", "id ="+str(ID))
#row_num = Select_column("total_records","users_dataset", "id ="+str(ID))
#summary = eval((column_summary[0][0]).replace('null', 'None'))
#consistent_num(df['week_ending'].tolist())
#df1 = pd.DataFrame(df['patients'].tolist(),columns = 'patients')
#print(df['patients'].isnull().values.any())
#print(summary)
#summary['areaCode'] = summary.pop('u00efu00bbu00bfareaCode')
"""for col, summ in summary.items():
		summ = summ[:7]
		if summ[5] == 'str':
			summ.append(consistent_num(df[col].tolist()))
		else:
			summ.append(row_num[0][0])
		summary[col] = summ
summary = str(summary).replace('None','null')
summary = summary.replace("'",'"')
summary = "'"+summary+"'"
#update("users_dataset","column_summary",summary,"id ="+str(ID))
print(summary)"""


"""print(path)
print(df.columns.tolist())"""

#update_consistency(4)