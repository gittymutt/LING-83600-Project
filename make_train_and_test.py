from gensim import corpora, models, similarities
import pickle

PICKLEPATH = "Pickles"

with open(PICKLEPATH+'/doc_nyt1.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    nyt_doc = pickle.load(f)

with open(PICKLEPATH+'/bb_docs.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    con_docs = pickle.load(f)

with open(PICKLEPATH+'/lib_docs.pickle', 'rb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    lib_docs = pickle.load(f)


con_train_set = con_docs[:10521]
con_test_set = con_docs[10521:]

lib_train_set = lib_docs[:4737]
lib_test_set = lib_docs[4737:]



with open('con_train_set.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(con_train_set, f, pickle.HIGHEST_PROTOCOL)

with open('con_test_set.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(con_test_set, f, pickle.HIGHEST_PROTOCOL)

with open('lib_train_set.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(lib_train_set, f, pickle.HIGHEST_PROTOCOL)

with open('lib_test_set.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(lib_test_set, f, pickle.HIGHEST_PROTOCOL)
