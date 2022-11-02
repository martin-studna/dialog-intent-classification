from ..component import Component
from ..dialogue import Dialogue
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import random

class IrAgent(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialize()

    def _initialize(self):
        keys = []
        values = []
        train_dataset = os.path.join(os.path.dirname(__file__), '../../data/dailydialog/dialogues_train.txt')
        with open(train_dataset, 'r') as f:
            for line in f:
                dialogue = line.strip().split('__eou__')
                dialogue = list(map(lambda x: x.strip(), dialogue))
                for key, value in zip(dialogue, dialogue[1:]):
                    keys.append(key)
                    values.append(value)

        self._values = values 
        self.vectorizer = TfidfVectorizer(ngram_range=(1,3))
        self._keys_mat = self.vectorizer.fit_transform(keys)


    def __call__(self, dial: Dialogue, logger):
        tfidf = self.vectorizer.transform([dial.user])
        score = cosine_similarity(self._keys_mat, tfidf)[:, 0]
        num_top = 10
        top = np.argpartition(-score, num_top)[:num_top]
        response = self._values[random.choice(top)]
        dial.system = response
        return dial

