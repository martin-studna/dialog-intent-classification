import sys
sys.path.insert(0, '..')
from dialmonkey.da import DA
from hw4.dialog_data import DialogData
from hw4.callback import NeptuneCallback
import tensorflow as tf
import numpy as np
import sklearn
from tensorflow.keras import preprocessing
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from tensorflow.python.keras.layers.preprocessing import text_vectorization
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


import neptune
from os import environ
import argparse
import os
import re


# Report only TF errors by default
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

'''
    The IntentSlotClassifier class implements the FeedForward neural network with tensorflow.
    It gets the user input as a sentence and it classifies which intents should be matched with the sentence.
    The sentences are vectorized with the dataset dictionary. The dictionary is created from all of the words in the dataset.
    If a word occurs in the sentence, our dictionary is going to give us the index in the input vector and at this position we will assign one.

    The output layer returns the vector distribution of all possible combinations of intent-slot-values. 
    The following maps are used for mapping words/targets on the indices and vice versa:
    
    `word_map`: (word) -> (index)
    `labels_map` (intent|slot|value|intent(slot)|intent(slot=value)) -> (index), 
                 (index) -> (intent|slot|value|intent(slot)|intent(slot=value))
'''


class IntentSlotClassifier:
    def __init__(self,
                 learning_rate=0.001,
                 batch_size=64,
                 dropout=0,
                 l2=0,
                 seed=42,
                 activation_function="relu",
                 batch_normalization=False,
                 label_smoothing=0,
                 hidden_layers=[],
                 threads=16):

        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.dropout = dropout
        self.l2 = l2
        self.seed = seed
        self.batch_normalization = batch_normalization
        self.label_smoothing = label_smoothing
        self.hidden_layers = hidden_layers
        self.threads = 16
        self.activation_function = activation_function

        self.model = None

    '''
        Predicts the intent-slot pair for single sentence.
    '''

    def predict(self, string):

        result = self.model.predict(np.array([string]))
        print(string)
        prediction = {}
        slot_prediction = {}
        for i in range(len(result[0])):
            if result[0][i] >= 0.05:
                intent = self.labels_map[i].lower().split('-')
                if len(intent) == 1:
                    prediction[intent[0]] = {}
                    slot_prediction[intent[0]] = {}
                elif len(intent) == 2:
                    if intent[0] not in prediction:
                        prediction[intent[0]] = {intent[1]: None}
                        slot_prediction[intent[0]] = {intent[1]: None}
                    elif intent[1] not in prediction[intent[0]]:
                        prediction[intent[0]][intent[1]] = None
                        slot_prediction[intent[0]][intent[1]] = None
                elif len(intent) == 3:
                    if intent[0] not in prediction:
                        prediction[intent[0]] = {intent[1]: intent[2]}
                        slot_prediction[intent[0]] = {
                            intent[1]: {intent[2]: result[0][i]}}
                    elif intent[1] not in prediction[intent[0]]:
                        prediction[intent[0]][intent[1]] = intent[2]
                        slot_prediction[intent[0]][intent[1]] = {
                            intent[2]: result[0][i]}

        string = self.get_string(prediction)
        print("DA: ", string)

        da = DA.parse_cambridge_da(string)

        for dai in da.dais:
            if dai.intent in slot_prediction \
                    and slot_prediction[dai.intent] is not None and dai.slot in slot_prediction[dai.intent] \
                    and slot_prediction[dai.intent][dai.slot] is not None and dai.value in slot_prediction[dai.intent][dai.slot]:

                dai.confidence = slot_prediction[dai.intent][dai.slot][dai.value]

        return da

    def predict_file(self):

        dialogs = DialogData()

        predictions = self.model.predict(dialogs.test.data["utterances"])

        predictions = np.where(predictions >= 0.5, 1, 0)

        with open('predicted.txt', 'w') as writer:
            for i in range(predictions.shape[0]):
                prediction = {}
                for j in range(predictions.shape[1]):
                    if predictions[i][j] == 1:
                        intent = self.labels_map[j].split('-')
                        if len(intent) == 1:
                            prediction[intent[0]] = {}
                        elif len(intent) == 2:
                            if intent[0] not in prediction:
                                prediction[intent[0]] = {intent[1]: None}
                            elif intent[1] not in prediction[intent[0]]:
                                prediction[intent[0]][intent[1]] = None
                        elif len(intent) == 3:
                            if intent[0] not in prediction:
                                prediction[intent[0]] = {intent[1]: intent[2]}
                            elif intent[1] not in prediction[intent[0]]:
                                prediction[intent[0]][intent[1]] = intent[2]

                string = self.get_string(prediction)
                if string != '':
                    writer.write(string + '\n')
                else:
                    writer.write('None' + '\n')

    '''
        Merges dictionaries.
    '''

    def merge_dicts(self, dict1, dict2):

        z = dict1

        for k in set(dict1.keys()).union(dict2.keys()):
            if k in dict1 and k in dict2:
                for k2 in set(dict1[k].keys()).union(dict2[k].keys()):
                    if k2 in dict1[k] and k2 in dict2[k]:
                        z[k][k2] = list(set(dict1[k][k2])) + \
                            list(set(dict2[k][k2]))
                    elif k2 not in dict1[k]:
                        z[k][k2] = dict2[k][k2]
            elif k not in dict1:
                z[k] = dict2[k]

        return z

    '''
        Parses intent slots and values from the input.
    '''

    def parse_intents(self, das_strings):
        data = []
        dai_dict = {}
        for das_string in das_strings:
            da = DA.parse_cambridge_da(das_string)
            for dai in da.dais:
                if dai.intent not in dai_dict and dai.intent is not None:
                    dai_dict[dai.intent] = {}
                if dai.slot not in dai_dict[dai.intent] and dai.slot is not None:
                    dai_dict[dai.intent][dai.slot] = []

                if dai.value is not None:
                    dai_dict[dai.intent][dai.slot].append(dai.value)

        for intent_key in dai_dict:
            for slot_key in dai_dict[intent_key]:
                if len(dai_dict[intent_key][slot_key]) > 0:
                    dai_dict[intent_key][slot_key].append('null')
                dai_dict[intent_key][slot_key] = np.unique(
                    np.array(dai_dict[intent_key][slot_key]))

        return dai_dict

    '''
        Converts dictionary to DA string
    '''

    def get_string(self, prediction):
        string = ""
        first_intent = True
        first_attr = True
        for intent in prediction.keys():
            if first_intent is False:
                string += '|'
            string += intent + '('
            first_intent = False
            for attr in prediction[intent].keys():
                if first_attr is False:
                    string += ','
                if prediction[intent][attr] is None:
                    string += attr
                else:
                    string += attr + '=' + prediction[intent][attr]

                first_attr = False
            string += ')'

            first_attr = True
        return string

    '''
        Trains the neural net. It also returns predicted.txt file.
    '''

    def train(self, epochs=10):
        # neptune.init(project_qualified_name='martin.studna/dialmonkey')
        np.random.seed(self.seed)
        tf.random.set_seed(self.seed)
        # tf.config.threading.set_inter_op_parallelism_threads(self.threads)

        dialogs = DialogData()

        loss = tf.losses.BinaryCrossentropy(
            label_smoothing=self.label_smoothing)

        # Vocabulary size and number of words in a sequence.
        vocab_size = len(dialogs.train.dictionary.keys())
        sequence_length = 10

        # Use the text vectorization layer to normalize, split, and map strings to
        # integers. Note that the layer uses the custom standardization defined above.
        # Set maximum_sequence length as all samples are not of the same length.
        vectorize_layer = TextVectorization(
            max_tokens=vocab_size,
            output_mode='int',
            pad_to_max_tokens=True,
            output_sequence_length=sequence_length)

        PARAMS = {
            'hidden_layers': self.hidden_layers,
            'dropout': self.dropout,
            'activation function': self.activation_function,
            'l2': self.l2,
            'batch normalization': self.batch_normalization,
            'learning rate': self.learning_rate,
            'loss': loss,
            'batch_size': self.batch_size,
            'label_smoothing': self.label_smoothing,
            'epochs': epochs,
        }

        # neptune.create_experiment(params=PARAMS)

        labels_train = self.parse_intents(dialogs.train.data["das"])
        labels_dev = self.parse_intents(dialogs.dev.data["das"])
        labels_test = self.parse_intents(dialogs.test.data["das"])

        labels_dict = self.merge_dicts(
            labels_train, self.merge_dicts(labels_dev, labels_test))

        labels_map = {}

        index = 0
        for intent, i in zip(labels_dict.keys(), range(len(labels_dict.keys()))):
            labels_map[intent] = index
            labels_map[index] = intent
            index += 1
            for slot, j in zip(labels_dict[intent].keys(), range(len(labels_dict[intent].keys()))):
                labels_map[intent + '-' + slot] = index
                labels_map[index] = intent + '-' + slot
                index += 1
                for k in range(len(labels_dict[intent][slot])):
                    labels_map[intent + '-' + slot + '-' +
                               labels_dict[intent][slot][k]] = index
                    labels_map[index] = intent + '-' + slot + \
                        '-' + labels_dict[intent][slot][k]
                    index += 1

        self.labels_map = labels_map

        labels_train_ids = np.zeros(
            (len(dialogs.train.data["das"]), index + 1))
        labels_dev_ids = np.zeros(
            (len(dialogs.dev.data["das"]), index + 1))
        labels_test_ids = np.zeros(
            (len(dialogs.test.data["das"]), index + 1))

        for i in range(len(dialogs.train.data["das"])):
            da = DA.parse_cambridge_da(dialogs.train.data["das"][i])
            for dai in da.dais:
                if dai.slot is None:
                    labels_train_ids[i][labels_map[dai.intent]] = 1
                elif dai.slot is not None and dai.value is None:
                    labels_train_ids[i][labels_map[dai.intent +
                                                   '-' + dai.slot]] = 1
                else:
                    labels_train_ids[i][labels_map[dai.intent +
                                                   '-' + dai.slot + '-' + dai.value]] = 1

        for i in range(len(dialogs.dev.data["das"])):
            da = DA.parse_cambridge_da(dialogs.dev.data["das"][i])
            for dai in da.dais:
                if dai.slot is None:
                    labels_dev_ids[i][labels_map[dai.intent]] = 1
                elif dai.slot is not None and dai.value is None:
                    labels_dev_ids[i][labels_map[dai.intent +
                                                 '-' + dai.slot]] = 1
                else:
                    labels_dev_ids[i][labels_map[dai.intent +
                                                 '-' + dai.slot + '-' + dai.value]] = 1

        for i in range(len(dialogs.test.data["das"])):
            da = DA.parse_cambridge_da(dialogs.test.data["das"][i])
            for dai in da.dais:
                if dai.slot is None:
                    labels_test_ids[i][labels_map[dai.intent]] = 1
                elif dai.slot is not None and dai.value is None:
                    labels_test_ids[i][labels_map[dai.intent +
                                                  '-' + dai.slot]] = 1
                else:
                    labels_test_ids[i][labels_map[dai.intent +
                                                  '-' + dai.slot + '-' + dai.value]] = 1

        '''
            Create ids from words of the data dictionary.
        '''

        vectorize_layer.adapt(list(dialogs.train.dictionary.keys()))

        embedding_dim = 5

        l1l2_regularizer = None

        if self.l2 != 0:
            l1l2_regularizer = tf.keras.regularizers.L1L2(l1=0, l2=self.l2)

        '''
            The input layer
        '''

        model = tf.keras.Sequential([
            vectorize_layer,
            tf.keras.layers.Embedding(
                vocab_size, embedding_dim, name="embedding"),
            # tf.keras.layers.GlobalAveragePooling1D(),

        ])

        '''
            Hidden layers
        '''
        model.add(tf.keras.layers.Flatten())
        for hidden_layer in self.hidden_layers:
            model.add(tf.keras.layers.Dense(hidden_layer,
                                            activation=self.activation_function, kernel_regularizer=l1l2_regularizer))

            if self.dropout != 0:
                model.add(tf.keras.layers.Dropout(self.dropout))

            if self.batch_normalization:
                model.add(tf.keras.layers.BatchNormalization())

        '''
            The output layer
        '''

        # tf.keras.layers.Dense(embedding_dim, activation=tf.nn.relu)
        model.add(tf.keras.layers.Dense(index + 1,
                                        activation=tf.nn.sigmoid, kernel_regularizer=l1l2_regularizer))

        model.compile(
            optimizer=tf.optimizers.Adam(self.learning_rate),
            loss=loss,
            metrics=[tf.metrics.BinaryAccuracy(name="accuracy")],
        )

        model.fit(dialogs.train.data["utterances"], labels_train_ids, batch_size=self.batch_size, shuffle=True,
                  validation_data=(dialogs.dev.data["utterances"], labels_dev_ids), epochs=epochs)

        model.summary()

        self.model = model
