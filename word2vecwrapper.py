import gensim
from sklearn import preprocessing
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.metrics.pairwise import euclidean_distances

########################
# To vectorize the data
#########################

# Are not allowed to be in synonym clusters
NO_MATCH = set(["polio", "measles", "measle"])

class Word2vecWrapper:
    """
    Word2vecWrapper 
    A class for storing the information regarding the distributional semantics space
    """

    def __init__(self, model_path, semantic_vector_length):
        self.word2vec_model = None
        self.model_path = model_path
        self.semantic_vector_length = semantic_vector_length
        self._vocabulary_list = None

        if semantic_vector_length is not None:
            self.default_vector = [0] * self.semantic_vector_length

        self.empty_vector = None
        self.nearest_centroid_clf = None
    
    def load(self):
        """
        load the semantic space in the memory
        """
        if self.word2vec_model == None:
            print("Loading word2vec model, this might take a while ....")
            self.word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(self.model_path, binary=True)
            print("Loaded word2vec model")

    def get_semantic_vector_length(self):
        return self.semantic_vector_length

    def end(self):
        """
        remove the semantic space from the memory
        """
        self.word2vec_model = None
        gc.collect()


    def set_vocabulary(self, vocabulary_list):
        #if self._vocabulary_list is None:
        if True:
            self._vocabulary_list = []            
            for el in vocabulary_list:
                if len(el) == 3 and el[1] == "_":
                    self._vocabulary_list.append(el[0])
                else:
                    self._vocabulary_list.append(el)
            print("Vocabulary list length " + str(len(self._vocabulary_list)))

    def get_vector(self, word):
        if len(word) == 3 and word[1] == "_":
            word = word[0] # To cover for a bug in scikit learn, one char tokens have been transformed to longer. These are here transformed back
        
        #print("word, in word2vec wrapper", word)
        try:
            self.load()
            raw_vec = self.word2vec_model[word]
            if len(raw_vec) != self.semantic_vector_length:
                print("The true semantic vector has length " + str(len(raw_vec)))
                print("while the configuration file states that is should have length " + str(self.semantic_vector_length))
                exit(1)
            return raw_vec
        except KeyError:
            return self.default_vector
        
    def load_clustering(self):
        print("Clustering vectors, this might take a while ....")
        if self._vocabulary_list is None:
            raise Exception("set_vocabulary is not yet run")

        X_vectors = []
        cluster_words = []
        for word in self._vocabulary_list:
            vector = self.get_vector(word)
            if not all([el1 == el2 for el1, el2 in zip(vector, self.default_vector)]):
                norm_vector = preprocessing.normalize(np.reshape(vector, newshape = (1, self.semantic_vector_length)), norm='l2') # normalize the vector (l2 = eucledian)  
                list_vector = norm_vector[0]
                X_vectors.append(list_vector)
                cluster_words.append(word)

        # Compute DBSCAN
        X = np.matrix(X_vectors)
        self.cluster_dict = {}
        db = DBSCAN(eps=0.8, min_samples=1).fit(X)
        labels = db.labels_

        for label, term, vector in zip(labels, cluster_words, X_vectors):
            if term in NO_MATCH: # User defined to exclude from clustering
                continue
            if label != -1:                
                if label not in self.cluster_dict:
                    self.cluster_dict[label] = []
                self.cluster_dict[label].append(term)

        self.term_similar_dict = {}
        for label, items in self.cluster_dict.items():
            if len(items) > 1:
                for term in items:
                    self.term_similar_dict[term] = "_".join(items)

        for item in list(set(self.term_similar_dict.values())):
            print(item)
           
        self.nr_of_clusters = len(set(labels)) 
        print("Clustered vectors")
        

    def get_similars(self, word):
        try: # TODO: Check that all is initialised here
            similars = self.term_similar_dict[word]
            return similars
        except KeyError:
            return word
        
