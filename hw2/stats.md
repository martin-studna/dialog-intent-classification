# Dataset exploration

This document makes further analysis of statistics results from bAbi Tasks 5 and 6.

First, we should discuss how the dialogs from the task 5 differs from the dialogs from the task 6:

- Task 5 dialogs have the same number of the user and the bot turns, while task 6 dialogs do not have.
- Task 6 has more dialogs than task 5.
- In both tasks bots have more spoken words.
- The vocabulary of the user is significantly smaller than the bot vocabulary in the task 5, while in the task 6 vocabularies both of them have similar sizes.

Another thing we can notice that Shannon entropy and Conditional entropy are always bigger when the vocabulary size is also bigger. We can say that entropy is "the measurement of surprise". If there is an event, which is not most likely to happen, it is more surprising for us and its entropy is bigger.

Text entropy depends on, how frequently is each word used in the text. We would say that, if we have a bigger vocabulary, then we can have a text with less frequently used words, which means that each word will also have a smaller probability. This also means that we will have a bigger entropy.

We would say that the main difference between tasks 5 and 6 is, that in the task 5 the user asks more straightforward/simple and short questions, while in the task 6 he asks more sophisticated and longer questions. This is probably the reason why the user's vocabulary is smaller in the task 5 than in the task 6.

### Task 5

```
Total number of dialogs: 1000
Total number of turns: 25872

Total number of user turns: 12936
Total number of bot turns: 12936

Total number of user words: 87378
Total number of bot words: 145312

The mean of the number of turns per dialog: 25.872
The mean of the number of user turns per dialog: 12.936
The mean of the number of bot turns per dialog: 12.936

The standard deviation of the number of turns per dialog: 3.298952502840855
The standard deviation of the number of user turns per dialog: 1.6494762514204275
The standard deviation of the number of bot turns per dialog: 1.6494762514204275

The mean of the number of words in turn: 8.993893011750155
The mean of the number of user words in turn: 3.3773191094619666
The mean of the number of bot words in turn: 5.616573902288188

The standard deviation of the number of words in turn: 41.19070173455756
The standard deviation of the number of user words in turn: 9.080899262134507
The standard deviation of the number of bot words in turn: 11.73395964001679

Total vocabulary size: 1037
User vocabulary size: 103
Bot vocabulary size: 978

Total Shannon Entropy: 6.75662863690587
User Shannon Entropy: 5.93774907219255
Bot Shannon Entropy: 6.253485442601768

Total Conditional Shannon Entropy: 0.9611147022511761
User Conditional Shannon Entropy: 0.7049882297147547
Bot Conditional Shannon Entropy: 0.7180166855762837
```

### Task 6

```
Total number of dialogs: 1618
Total number of turns: 22656

Total number of user turns: 10516
Total number of bot turns: 12140

Total number of user words: 62389
Total number of bot words: 169334

The mean of the number of turns per dialog: 14.00247218788628
The mean of the number of user turns per dialog: 6.49938195302843
The mean of the number of bot turns per dialog: 7.503090234857849

The standard deviation of the number of turns per dialog: 5.108525258320877
The standard deviation of the number of user turns per dialog: 2.546265202077389
The standard deviation of the number of bot turns per dialog: 2.5644037598831373

The mean of the number of words in turn: 10.227886652542374
The mean of the number of user words in turn: 2.753751765536723
The mean of the number of bot words in turn: 7.47413488700565

The standard deviation of the number of words in turn: 36.47907479004819
The standard deviation of the number of user words in turn: 6.213767852173573
The standard deviation of the number of bot words in turn: 10.03434283717917

Total vocabulary size: 992
User vocabulary size: 550
Bot vocabulary size: 603

Total Shannon Entropy: 6.921696402803485
User Shannon Entropy: 5.939730750969489
Bot Shannon Entropy: 6.602538798502655

Total Conditional Shannon Entropy: 1.2938794193114276
User Conditional Shannon Entropy: 0.794427029288706
Bot Conditional Shannon Entropy: 1.2424381770381572
```
