import pandas as pd
import json

#path = input("type your path : ")
df = pd.read_csv("/home/csimage/git/DataMarket/1-phe_deaths_age_london.csv")
data = df.to_json(orient='index')
my_dict=json.loads(data)
for line in my_dict.items():
    print(type(line))