import os
import sys
import urllib.request
import zipfile
import json
import re
import numpy as np


class DialogData:

    _URL = "https://ufal.mff.cuni.cz/~odusek/courses/npfl123/data/hw4_data.zip"

    class Dataset:
        def __init__(self, data, shuffle_batches, seed=42):
            utterances = np.array([o["usr"] for o in data])
            DAs = np.array([o["DA"] for o in data])

            self._data = {"utterances": [], "das": []}
            self._data["utterances"] = utterances
            self._data["das"] = DAs
            self._data_size = len(self._data["utterances"])
            self._label_size = len(self._data["das"])

            self._raw_text = ""

            for sentence in utterances:
                self._raw_text += ' ' + sentence

            freq_words = {}

            for sentence in self._data["utterances"]:
                for word in np.unique(re.sub('[,?.]', '', sentence).lower().split(' ')):
                    if word not in freq_words:
                        freq_words[word] = 1
                    else:
                        freq_words[word] += 1

            freq_words["UNK"] = 1

            self._freq_words = freq_words

            # freq_words = sorted(
            #     freq_words, key=freq_words.get, reverse=True)

            # if len(freq_words) >= 1000:
            #     freq_words = freq_words[:1000]

            # f_dict = {}
            # for i in range(len(freq_words)):
            #     f_dict[freq_words[i]] = i

            self._shuffler = np.random.RandomState(
                seed) if shuffle_batches else None

        @property
        def dictionary(self):
            return self._freq_words

        @property
        def raw_text(self):
            return self._raw_text

        @property
        def data(self):
            return self._data

        @property
        def data_size(self):
            return self._data_size

        @property
        def label_size(self):
            return self._label_size

        def batches(self, size=None):
            permutation = self._shuffler.permutation(
                self._size) if self._shuffler else np.arange(self._size)
            while len(permutation):
                batch_size = min(size or np.inf, len(permutation))
                batch_perm = permutation[:batch_size]
                permutation = permutation[batch_size:]

                batch = {}
                for key in self._data:
                    batch[key] = self._data[key][batch_perm]
                yield batch

    def __init__(self):
        path = os.path.basename(self._URL)
        if not os.path.exists(path):
            print("Downloading dataset {}...".format(path), file=sys.stderr)
            urllib.request.urlretrieve(self._URL, filename=path)
        with zipfile.ZipFile(path, "r") as zip_file:
            zip_file.extractall(os.path.dirname(os.path.abspath(__file__)))
            for dataset in ["train", "dev", "test"]:
                with zip_file.open("dstc2-nlu-{}.json".format(dataset), "r") as dataset_file:
                    data = json.load(dataset_file)
                setattr(self, dataset, self.Dataset(
                    data,
                    shuffle_batches=dataset == "train",
                ))
        os.remove(path)
