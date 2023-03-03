import pandas as pd
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import Counter
from nltk.corpus import wordnet

stop_word = set(stopwords.words('english'))
ps = PorterStemmer()

#extact the key word from the sentence and output dict_keys
def extact(sentence):
  #lower case of whole sentence
  sentence = sentence.casefold()
  word_list = re.split('[\W_]+', sentence)
  regex = re.compile('[^a-zA-Z]')
  i = 0
  for item in word_list:
       #Romove non-letter characters to be ""
       word_list[i] = regex.sub('', item)
       item = word_list[i]
       if item in stop_word:
              word_list[i] = ""
       else:
              word_list[i] = ps.stem(item)
       i += 1
  result = list(filter(None, word_list)) #delete all none element
  #result = list(Counter(word_list))

  if '' in result:
    result.remove('')
  return result

def synonyms(word):
       #get the synonyms of the word
       synonyms = []
       for syn in wordnet.synsets(word):
           for lm in syn.lemmas():
                    synonyms.append(lm.name())
       return synonyms[:10]
       

