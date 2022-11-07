import pandas as pd
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import Counter
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Kilburn",
  database="datamarket"
)

stop_word = set(stopwords.words('english'))
ps = PorterStemmer()

#extact the key word from the sentence and output dict_keys
def extact(sentence):
  #Romove non-letter characters
  word_list = sentence.split()
  regex = re.compile('[^a-zA-Z]')
  i = 0
  for item in word_list:
       word_list[i] = regex.sub('', item)
       item = word_list[i]
       if item in stop_word:
              word_list[i] = ""
       else:
              word_list[i] = ps.stem(item.casefold())
       i += 1
  result = list(Counter(word_list))
  result.remove('')
  return result


"""def input_database(items):
  mycursor = mydb.cursor()
  for item in items:
    mycursor.execute("INSERT INTO Keyword_Inverted_Index (keyword, dataset_id) VALUES (%s, %d)", ())"""

#miss the put in the database


df = pd.read_excel("/home/csimage/git/DataMarket/0-Datasets-Metadata.xlsx")
title = df["Description"]
#i = " on 03 August 2022."
#print(title[0])
print(extact(title[0]))
#print(extact(i))

