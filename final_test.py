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
    con_train_set = pickle.load(f)

with open(PICKLEPATH+'/con_test_set.pickle', 'rb') as f:
    con_test_set = pickle.load(f)

with open(PICKLEPATH+'/lib_test_set.pickle', 'rb') as f:
    lib_test_set = pickle.load(f)

with open(PICKLEPATH+'/lib_train_set.pickle', 'rb') as f:
    lib_train_set = pickle.load(f)

with open(PICKLEPATH+'/doc_wsj1.pickle', 'rb') as f:
    lib_doc = pickle.load(f)

# cutoff for last con doc. Libdocs start at this index
train_cutoff = len(con_train_set)
test_cutoff = len(con_test_set)

train_set = con_train_set + lib_train_set

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

print("creating query bow...")
vec_bow_array = [lib_dictionary.doc2bow(doc) for doc in test_set]

vec_bow_array = [lib_tfidf[bow] for bow in vec_bow_array]
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

print ("Performing similarity query")
# lib_sims = lib_index[lib_vec_lsi] # perform a similarity query against the corpus
lib_sims_array = [lib_index[vec] for vec in vec_lsi_array] # perform a similarity query against the corpus
# lib_sims.save('Temp/similarity_query_with_wsj1')


# lib_best = sorted(enumerate(lib_sims), key=lambda item: -item[1])
lib_best_array = [sorted(enumerate(lib_sims), key=lambda item: -item[1]) for lib_sims in lib_sims_array]


# choose the closest matches



# print (lib_best[:20])
results = []
total_con_docs = 0
total_lib_docs = 0
total_lib_score = 0
total_con_score = 0
top_100_results = []


for i in range(len(lib_best_array)):
    best = lib_best_array[i]
    no_con_docs = len ([c for c in best[:100] if c[0]< train_cutoff] )
    if i < test_cutoff:
        classification = 'C'
        total_con_docs=total_con_docs+1
        total_con_score = total_con_score + no_con_docs
        top_100_results.append((classification, no_con_docs))
    else:
        classification = 'L'
        total_lib_docs = total_lib_docs+1
        total_lib_score = total_lib_score+100-no_con_docs
        top_100_results.append((classification, no_con_docs))
    print (classification, ": ", no_con_docs)


with open('top_100_results.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(top_100_results, f, pickle.HIGHEST_PROTOCOL)


print ("Average score for con docs:", total_con_score/total_con_docs)
print ("Average score for lib docs:", total_lib_score/total_lib_docs)
print("highest liberal score:")
print (lib_best[:10])
print("highest conservative score:")
print (con_best[:10])
