"""
Test using the test set instead of just one document. Evaluate model.
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
    con_train_set = pickle.load(f)

with open(PICKLEPATH+'/con_test_set.pickle', 'rb') as f:
    con_test_set = pickle.load(f)

with open(PICKLEPATH+'/lib_test_set.pickle', 'rb') as f:
    lib_test_set = pickle.load(f)

with open(PICKLEPATH+'/lib_train_set.pickle', 'rb') as f:
    lib_train_set = pickle.load(f)

with open(PICKLEPATH+'/doc_wsj1.pickle', 'rb') as f:
    lib_doc = pickle.load(f)

# take 1000 samples from con training set to make another test set
con_test_set2 = con_train_set[-1000:]
con_train_set = con_train_set[:-1000]

# take 500 samples from lib training set to make another test sent_tokenize
lib_test_set2 = lib_train_set[-500:]
lib_train_set = lib_train_set[:-500]

# cutoff for last con doc. Libdocs start at this index
train_cutoff = len(con_train_set)
test_cutoff = len(con_test_set)
test2_cutoff = len(con_test_set2)

train_set = con_train_set + lib_train_set

# make small testing test set
test_set = con_test_set + lib_test_set
test_set2 = con_test_set2 + lib_test_set2

# Comment the .load line and uncomment the others around it
# to create new models instead of loading pre-made model
#################
# lib_dictionary = corpora.Dictionary(train_set)
lib_dictionary = corpora.Dictionary.load('Temp/dictionary')
# lib_dictionary.save('Temp/dictionary')
print ("Created dictionary")

print ("Creating bow...")
lib_corpus = [lib_dictionary.doc2bow(text) for text in train_set]
print ("Created bow")

# Comment the .load line and uncomment the others around it
# to create new models instead of loading pre-made model
#################
print("creating tfidf model...")
# lib_tfidf = models.TfidfModel(lib_corpus)
lib_tfidf = models.TfidfModel.load('Temp/tfidfmodel')
# lib_tfidf.save('Temp/tfidfmodel')

print ("Created TfidfModel")

print("creating query bow...")
vec_bow_array = [lib_dictionary.doc2bow(doc) for doc in test_set]
vec_bow_array2 = [lib_dictionary.doc2bow(doc) for doc in test_set2]

vec_bow_array = [lib_tfidf[bow] for bow in vec_bow_array]
vec_bow_array2 = [lib_tfidf[bow] for bow in vec_bow_array2]
print ("Created query bow")


print ("Creating tfidf corpus...")
lib_corpus_tfidf = lib_tfidf[lib_corpus]
print ("Created tfidf corpus")

# Comment the .load line and uncomment the others around it
# to create new models instead of loading pre-made model
###########################
print( "Creating lsi model for corpus...")
# lib_lsi = models.LsiModel(lib_corpus_tfidf, id2word=lib_dictionary, num_topics=500)
lib_lsi = models.LsiModel.load('Temp/lib_lsi.lsi')
# lib_lsi.save('Temp/lib_lsi.lsi')
print ("Created lsi model")

vec_lsi_array = [lib_lsi[vec] for vec in vec_bow_array] # convert the query to LSI space
vec_lsi_array2 = [lib_lsi[vec] for vec in vec_bow_array2] # convert the query to LSI space
print ("Created query vec lsi")

# Comment the .load line and uncomment the others around it
# to create new models instead of loading pre-made model
###########################
print ("Creating similarity Matrix")
# lib_index = similarities.MatrixSimilarity(lib_lsi[lib_corpus_tfidf], num_features=500) # transform corpus to LSI space and index it
lib_index = similarities.MatrixSimilarity.load('Temp/similarity_index500-sw-cf')
# lib_index.save('Temp/similarity_index500-sw-cf')

print ("Performing similarity query")
lib_sims_array = [lib_index[vec] for vec in vec_lsi_array] # perform a similarity query against the corpus
lib_sims_array2 = [lib_index[vec] for vec in vec_lsi_array2] # perform a similarity query against the corpus


lib_best_array = [sorted(enumerate(lib_sims), key=lambda item: -item[1]) for lib_sims in lib_sims_array]
lib_best_array2 = [sorted(enumerate(lib_sims), key=lambda item: -item[1]) for lib_sims in lib_sims_array2]

"""
with open(TEMPPATH+'/lib_best_array2.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(lib_best_array, f)
"""
# choose the closest matches
print("Comparing...")


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


with open('top_100_results.pickle', 'wb') as f:
    pickle.dump(top_100_results, f)


print ("Average score for test con docs:", total_con_score/total_con_docs)
print ("Average score for test lib docs:", total_lib_score/total_lib_docs)


# record successes and failiures

total_docs = len(lib_best_array2)
total_con_docs2 = 1000
total_lib_docs2 = 500

for threshold in range(17,90,5):
    concon = 0
    conlib = 0
    liblib = 0
    libcon = 0

# count the classified docs
    for i in range(len(lib_best_array2)):
        best = lib_best_array2[i]
        no_con_docs = len ([c for c in best[:100] if c[0]< train_cutoff] )
        no_lib_docs = 100-no_con_docs
        # Docs lower than test_cutoff are con docs
        if i < test_cutoff:
            # test whether it's above the threshold
            if no_con_docs > threshold:
                concon += 1
            else:
                conlib += 1
        else:
            if no_con_docs <= threshold:
                liblib += 1
            else:
                libcon += 1

    print (" ")

    print ("With threshold: ", threshold)

    print ("Confusion Matrix:")
    print (concon, " | ", conlib)
    print ("--------------------")
    print (libcon, " | ", liblib)
    print (" ")
    print ("Accuracy: ", (concon+liblib)/total_docs)
    print ("Misclassification Rate: ", (conlib+libcon)/total_docs)
    print ("True positive(con): ", concon/total_con_docs2)
    print ("True negative(lib): ", liblib/total_lib_docs2)
    print ("False positive(con): ", conlib/total_con_docs2)
    print ("False negative(lib): ", libcon/total_lib_docs2)

    print ("+++++++++++++++++++++++++++++")
    print (" ")
