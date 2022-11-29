import pandas as pd
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import Counter

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
  if '' in result:
    result.remove('')
  return result

