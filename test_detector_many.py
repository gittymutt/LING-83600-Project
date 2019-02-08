"""
test using the test set instead of just one document
"""

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
TEMPPATH = "Temp"

with open(PICKLEPATH+'/con_train_set.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    con_train_set = pickle.load(f)

with open(PICKLEPATH+'/con_test_set.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    con_test_set = pickle.load(f)

with open(PICKLEPATH+'/lib_test_set.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    lib_test_set = pickle.load(f)

with open(PICKLEPATH+'/lib_train_set.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    lib_train_set = pickle.load(f)

with open(PICKLEPATH+'/doc_wsj1.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    lib_doc = pickle.load(f)

# cutoff for last con doc. Libdocs start at this indexes
train_cutoff = len(con_train_set)
test_cutoff = len(con_test_set)

train_set = con_train_set + lib_train_set
# test_set = con_test_set + lib_test_set

# make small testing test set
test_set = con_test_set + lib_test_set

# lib_dictionary = corpora.Dictionary(train_set)
lib_dictionary = corpora.Dictionary.load('Temp/dictionary')
# lib_dictionary.save('Temp/dictionary')
print ("Created dictionary")

print ("Creating bow...")
lib_corpus = [lib_dictionary.doc2bow(text) for text in train_set]
print ("Created bow")

print("creating tfidf model...")
# lib_tfidf = models.TfidfModel(lib_corpus)
lib_tfidf = models.TfidfModel.load('Temp/tfidfmodel')
# lib_tfidf.save('Temp/tfidfmodel')

print ("Created TfidfModel")
# doc = "real obamacare challenges are a bit tricky"
# vec_bow = dictionary.doc2bow(doc.lower().split())

print("creating query bow...")
# doc = sents_tokenized[3]
# lib_vec_bow = lib_dictionary.doc2bow(lib_doc)
vec_bow_array = [lib_dictionary.doc2bow(doc) for doc in test_set]

vec_bow_array = [lib_tfidf[bow] for bow in vec_bow_array]
# lib_vec_bow = lib_tfidf[lib_vec_bow]
print ("Created query bow")


print ("Creating tfidf corpus...")
lib_corpus_tfidf = lib_tfidf[lib_corpus]
print ("Created tfidf corpus")

print( "Creating lsi model for corpus...")
# lib_lsi = models.LsiModel(lib_corpus_tfidf, id2word=lib_dictionary, num_topics=500)
lib_lsi = models.LsiModel.load('lib_lsi.lsi')
print ("Created lsi model")

vec_lsi_array = [lib_lsi[vec] for vec in vec_bow_array] # convert the query to LSI space
print ("Created query vec lsi")



print ("Creating similarity Matrix")
# lib_index = similarities.MatrixSimilarity(lib_lsi[lib_corpus_tfidf], num_features=500) # transform corpus to LSI space and index it
lib_index = similarities.MatrixSimilarity.load('Temp/similarity_index500-sw-cf')
# lib_index.save('Temp/similarity_index500-sw-cf')
# lib_index = similarities.MatrixSimilarity.load('index500-sw-cf')

print ("Performing similarity query")
# lib_sims = lib_index[lib_vec_lsi] # perform a similarity query against the corpus
lib_sims_array = [lib_index[vec] for vec in vec_lsi_array] # perform a similarity query against the corpus
# lib_sims.save('Temp/similarity_query_with_wsj1')


# lib_best = sorted(enumerate(lib_sims), key=lambda item: -item[1])
lib_best_array = [sorted(enumerate(lib_sims), key=lambda item: -item[1]) for lib_sims in lib_sims_array]


# choose the closest matches



# print (lib_best[:20])
results = []

print ("number of conservative docs in the top 100:")
for best in lib_best_array:
    no_con_docs = len ([c for c in best[:100] if c[0]< train_cutoff] )

    # account for the fact that there are more con doc than lib docs
    ratio = len(lib_train_set)/len(con_train_set)
    print ("ratio lib/con:", ratio*no_con_docs)
    results.append(ratio*no_con_docs)

print (sum(results[:test_cutoff]) / len(results[:test_cutoff]), sum(results[test_cutoff:])/len(results[test_cutoff:]))

# enumerated = list(enumerate(sims)) # print (document_number, document_similarity) 2-tuples
# best = max(enumerated, key=operator.itemgetter(1))

# lib_count = [c for c in lib_best where]

"""
print("highest liberal score:")
print (lib_best[:10])
print("highest conservative score:")
print (con_best[:10])
"""
