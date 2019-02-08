import re, nltk, json
import mysql.connector
from gensim.utils import tokenize
from nltk.corpus import stopwords
from detectormorse import ptbtokenizer
from gensim import corpora, models, similarities
stop_words = set(stopwords.words('english'))
import pickle

INPUTFILE = "vox_test_doc_2.txt"
OUTPUTFILE = "doc_vox2.pickle"
RAWPATH = "Rawtext"
PICKLEPATH = "Pickles"

text = ""
with open(RAWPATH + '/' + INPUTFILE, 'r') as f:
    text = f.read()

print(text)
# text = str(text)
sents = nltk.tokenize.sent_tokenize(text)
sents_tokenized = []
for s in sents:
    tokens = list(tokenize(s, lowercase=True))
    tokens = [t for t in tokens if t not in stop_words]
    sents_tokenized = sents_tokenized + tokens

print (sents_tokenized)

with open(PICKLEPATH + '/' + OUTPUTFILE, 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(sents_tokenized, f, pickle.HIGHEST_PROTOCOL)
"""
with open('doc_wsj1.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    data = pickle.load(f)



print(type(data))
"""
