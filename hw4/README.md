# 4. Statistical Natural Language Understanding

The solution for this task can be found in the following files:

- `hw4/da_classifier.py`  - IntentSlotClassifier model implementation.
- `hw4/train_classifier.py` - script for training the model.
- `hw4/dialog_data.py` - data component which loads data and create dataset. object
- `/dialmonkey/nlu/restaurant.py` - NLU for the restaurant domain.
- `/conf/restaurant.yaml` - configuration for the restaurant NLU.

### Statistics

- **PRECISION:   0.973**
- **RECALL:         0.776**
- **F-1:                  0.863**

The statistics above were achieved with the following command:

`/dialmonkey/evaluation/eval_nlu.py -r hw4/dstc2-nlu-test.json -p hw4/predicted.txt`

Our statistical natural language model is based on the Feedforward neural networks which were implemented with Tensorflow.

Our network has following architecture:

- **Input layer** - the size of the dictionary of the dataset.
- **Output layer** - the size of the number of all intent-slot-values combinations
- **2x hidden layers** each of them having  **800 neurons**.
- **2x Batch normalization layers**
- (Optionally) **Dropout layers**

The `IntentSlotClassifier` class implements the Feed-Forward Neural Network with tensorflow. It gets the user input as a sentence and it classifies which intents should be matched with the sentence. The sentences are vectorized with the dataset dictionary. The dictionary is created from all of the words in the dataset.

If a word occurs in the sentence, our dictionary is going to give us the index in the input vector and at this position, we will assign one. The output layer returns the vector distribution of all possible combinations of intent-slot-values.

The following maps are used for mapping words/targets on the indices and vice versa:

```
word_map:   (word) -> (index)
labels_map: (intent|slot|value|intent(slot)|intent(slot=value)) -> (index), 
            (index) -> (intent|slot|value|intent(slot)|intent(slot=value))
```

## Conclusion

We assume that better accuracy could be achieved by making the dictionary smaller. Our model has also another disadvantage that it knows only the words which are in the dataset dictionary. If we pass to our model a word that is not in the dictionary, we are going to get `unknown`. We could use some more efficient techniques for vectorizing the user utterances and combine them with word embedding.