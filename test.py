import pandas as pd
import json
import csv

#path = input("Enter a csv file address: ")
df = pd.read_csv(r'/home/csimage/git/DataMarket/industry_sic.csv')
data_file = open('/home/csimage/git/DataMarket/example.csv', 'w', newline='')
csv_writer = csv.writer(data_file)
#df = pd.read_csv(path)

data = df.to_json(orient='index')
#data = df.to_json()

my_dict=json.loads(data)
#print(type(my_dict))

for k in my_dict.items():
       data_string = json.dumps(k[1]) #data serialized
       #print(type(data_string))
       print(data_string)



