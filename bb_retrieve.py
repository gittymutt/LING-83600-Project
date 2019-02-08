import re, nltk, json
import mysql.connector
from gensim.utils import tokenize
from nltk.corpus import stopwords
from detectormorse import ptbtokenizer
from gensim import corpora, models, similarities
stop_words = set(stopwords.words('english'))
import pickle
import operator

PICKLEPATH = "Pickles"
ARCHIVEFILE = ""
TOPICS = 500


#### area under the curve
### stump classifier sklearn
### fasttext


with open(PICKLEPATH+'/doc_bb1.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    lib_doc = pickle.load(f)

with open(PICKLEPATH+'/doc_pscon1.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    con_doc = pickle.load(f)

with open(PICKLEPATH+'/bb_docs.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    con_sents_tokenized = pickle.load(f)

with open(PICKLEPATH+'/lib_docs.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    lib_sents_tokenized = pickle.load(f)

lib_dictionary = corpora.Dictionary(lib_sents_tokenized)
con_dictionary = corpora.Dictionary(con_sents_tokenized)
print ("Created dictionary")

lib_corpus = [lib_dictionary.doc2bow(text) for text in lib_sents_tokenized]
con_corpus = [con_dictionary.doc2bow(text) for text in con_sents_tokenized]
print ("Created bow")

# doc = "real obamacare challenges are a bit tricky"
# vec_bow = dictionary.doc2bow(doc.lower().split())

# Create query BOW
lib_vec_bow = lib_dictionary.doc2bow(lib_doc)
con_vec_bow = con_dictionary.doc2bow(lib_doc)
print ("Created query bow")

lib_tfidf = models.TfidfModel(lib_corpus)
con_tfidf = models.TfidfModel(con_corpus)
print ("Created TfidfModel")

lib_corpus_tfidf = lib_tfidf[lib_corpus]
con_corpus_tfidf = con_tfidf[con_corpus]
print ("Created tfidf corpus")

lib_lsi = models.LsiModel(lib_corpus_tfidf, id2word=lib_dictionary, num_topics=TOPICS)
con_lsi = models.LsiModel(con_corpus_tfidf, id2word=con_dictionary, num_topics=TOPICS)
print ("Created lsi model")

lib_vec_lsi = lib_lsi[lib_vec_bow] # convert the query to LSI space
con_vec_lsi = con_lsi[con_vec_bow] # convert the query to LSI space
print ("Created query vec lsi")



# print ("Creating similarity Matrix")
lib_index = similarities.MatrixSimilarity(lib_lsi[lib_corpus_tfidf], num_features=TOPICS) # transform corpus to LSI space and index it
con_index = similarities.MatrixSimilarity(con_lsi[con_corpus_tfidf], num_features=TOPICS) # transform corpus to LSI space and index it
print ("Creating similarity Matrix")

# put the same document in the indexes to compare
print ("Performing similarity query")
lib_sims = lib_index[lib_vec_lsi] # perform a similarity query against the corpus
con_sims = con_index[con_vec_lsi] # perform a similarity query against the corpus
# con_sims use lib vec or con vec_bow

lib_best = sorted(enumerate(lib_sims), key=lambda item: -item[1])
con_best = sorted(enumerate(con_sims), key=lambda item: -item[1])
# choose the closest matches


# enumerated = list(enumerate(sims)) # print (document_number, document_similarity) 2-tuples
# best = max(enumerated, key=operator.itemgetter(1))


print("highest liberal score:")
print (lib_best[:10])
print("highest conservative score:")
print (con_best[:10])
