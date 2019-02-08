import re, nltk, json
import mysql.connector
from gensim.utils import tokenize
from nltk.corpus import stopwords
from detectormorse import ptbtokenizer
from gensim import corpora, models, similarities
stop_words = set(stopwords.words('english'))
import pickle


mydb = mysql.connector.connect(
  host="localhost",
  user="user",
  passwd="&*%$(&*)",
  database="nytimes"
)

mycursor = mydb.cursor()

tables = ["breitbart_raw", "huffpost", "politico"]

docs = []

for table in tables:

    sql = "select text from " + table + ";"
    print(sql)
    try:
        mycursor.execute(sql)
        result = mycursor.fetchall()
    except Exception as e:
        print (e)
        print("************** db error ****************")

    print (len(result))
    count = 0
    for text in result:
        text = text[0]
        sents = nltk.tokenize.sent_tokenize(text)
        sents_tokenized = []
        for s in sents:
            tokens = list(tokenize(s, lowercase=True))
            tokens = [t for t in tokens if t not in stop_words]
            sents_tokenized = sents_tokenized + tokens
        print(count)
        count = count + 1
        # print (sents_tokenized)
        docs.append(sents_tokenized)
        sents_tokenized =[]
        # print ("-----------------------------")



with open('Pickles/conlib_docs.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(docs, f, pickle.HIGHEST_PROTOCOL)



with open('Pickles/conlib_docs.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)


print(type(data))
