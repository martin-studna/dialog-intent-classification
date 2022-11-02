#!/usr/bin/python3
import argparse
import sys
import re
import os
import math


parser = argparse.ArgumentParser()

parser.add_argument(
    "--file", default="./dialog-babi-task6-dstc2-trn-output.txt", type=str, help="Input file.")


'''
    Dict class extends classical python dictionary type with `push` method.
'''


class dict(dict):
    def push(self, w):
        if w in self:
            self[w] += 1
        else:
            self[w] = 1


'''
    Dialog class holds some important information about a dialog.
'''


class Dialog:

    def __init__(self):
        self.turns = 0
        self.words = 0
        self.user_words = 0
        self.bot_words = 0
        self.user_turns = 0
        self.bot_turns = 0
        self.number_of_user_words_per_turn = []
        self.number_of_bot_words_per_turn = []
        self.number_of_words_per_turn = []


def cond_entropy(bigrams, vocabulary, total_words):
    cond_entrop = 0
    for x in bigrams:
        for y in bigrams[x]:
            cond_entrop += (bigrams[x][y]/total_words) * \
                math.log2(bigrams[x][y]/vocabulary[x])

    return -cond_entrop


def shannon_entropy(vocabulary, total_words):
    return - sum([(y/total_words)*(math.log2(y/total_words)) for x, y in vocabulary.items()])


def push_bigrams(bigrams, tokens):
    for x, y in zip(tokens[2:], tokens[3:]):
        if x in bigrams and y in bigrams[x]:
            bigrams[x][y] += 1
        elif x in bigrams and y not in bigrams[x]:
            bigrams[x][y] = 1
        else:
            bigrams[x] = {y: 1}


def main(args):

    dialogs = open(args.file)

    dialog_count = 0
    total_turns = 0
    total_words = 0
    total_user_turns = 0
    total_bot_turns = 0
    total_user_words = 0
    total_bot_words = 0
    vocabulary = dict()
    user_vocabulary = dict()
    bot_vocabulary = dict()
    bigrams = {}
    user_bigrams = {}
    bot_bigrams = {}

    dialogs_stats = []
    stats = None
    for line in dialogs:
        if "DIALOG NUMBER" in line:
            dialog_count += 1
            if stats is not None:
                dialogs_stats.append(stats)
            stats = Dialog()
        elif line != "\n":
            total_turns += 1
            tokens = line.strip().split()
            total_words += len(tokens)
            stats.turns += 1
            stats.words += len(tokens)
            stats.number_of_words_per_turn.append(len(tokens))

            push_bigrams(bigrams, tokens)

            for w in tokens:
                vocabulary.push(w)
                if "USER:" in line:
                    user_vocabulary.push(w)
                if "BOT:" in line:
                    bot_vocabulary.push(w)

            if "USER:" in line:
                total_user_turns += 1
                total_user_words += len(tokens)
                stats.number_of_user_words_per_turn.append(len(tokens))
                stats.user_turns += 1
                stats.user_words += len(tokens)
                push_bigrams(user_bigrams, tokens)

            elif "BOT:" in line:
                total_bot_turns += 1
                total_bot_words += len(tokens)
                stats.number_of_bot_words_per_turn.append(len(tokens))
                stats.bot_turns += 1
                stats.bot_words += len(tokens)
                push_bigrams(bot_bigrams, tokens)

    dialogs.close()

    words_means = []
    user_words_means = []
    bot_words_means = []
    words_stds = []
    user_words_stds = []
    bot_words_stds = []

    stats_file = open(os.path.basename(
        args.file).split(".")[0] + '-stats.txt', 'w')
    stats_file.write(
        "The number of words in a turn for each dialog statistics:\n")
    count = 1
    for d in dialogs_stats:
        word_mean = d.words / d.turns
        user_word_mean = d.user_words / d.user_turns
        bot_word_mean = d.bot_words / d.bot_turns

        word_std = sum([math.pow(words - word_mean, 2)
                       for words in d.number_of_words_per_turn])
        user_word_std = sum([math.pow(words - user_word_mean, 2)
                            for words in d.number_of_user_words_per_turn])
        bot_word_std = sum([math.pow(words - bot_word_mean, 2)
                           for words in d.number_of_bot_words_per_turn])

        stats_file.write("Dialog " + str(count) + '\n')
        stats_file.write("Word mean: " + str(word_mean) + '\n')
        stats_file.write("User word mean: " + str(user_word_mean) + '\n')
        stats_file.write("Bot word mean: " + str(bot_word_mean) + '\n')

        stats_file.write("Word std: " + str(word_std) + '\n')
        stats_file.write("User word std: " + str(user_word_std) + '\n')
        stats_file.write("Bot word std: " + str(bot_word_std) + '\n\n')
        count += 1

        words_means.append(word_mean)
        user_words_means.append(word_mean)
        bot_words_means.append(word_mean)

        words_stds.append(word_std)
        user_words_stds.append(user_word_std)
        bot_words_stds.append(bot_word_std)

    stats_file.close()

    '''
        The mean of the number of turns in dialog
    '''
    turns_mean = total_turns / dialog_count
    user_turns_mean = total_user_turns / dialog_count
    bot_turns_mean = total_bot_turns / dialog_count

    '''
        The standard deviation of the number of turns in dialog
    '''
    turns_std = math.sqrt(sum([math.pow(x.turns - turns_mean, 2)
                          for x in dialogs_stats]) / dialog_count)
    user_turns_std = math.sqrt(sum([math.pow(
        x.user_turns - user_turns_mean, 2) for x in dialogs_stats]) / dialog_count)
    bot_turns_std = math.sqrt(sum(
        [math.pow(x.bot_turns - bot_turns_mean, 2) for x in dialogs_stats]) / dialog_count)

    '''
        The mean of the number of words in turn
    '''
    words_mean = total_words / total_turns
    user_words_mean = total_user_words / total_turns
    bot_words_mean = total_bot_words / total_turns

    '''
        The standard deviation of the number of words in turn
    '''

    words_std = math.sqrt(sum([math.pow(x.words - turns_mean, 2)
                          for x in dialogs_stats]) / total_turns)
    user_words_std = math.sqrt(sum([math.pow(
        x.user_words - user_words_mean, 2) for x in dialogs_stats]) / total_user_words)
    bot_words_std = math.sqrt(sum(
        [math.pow(x.bot_words - bot_words_mean, 2) for x in dialogs_stats]) / total_bot_words)

    '''
        Shannon Entropy
    '''

    total_shannon_entropy = shannon_entropy(vocabulary, total_words)
    user_shannon_entropy = shannon_entropy(user_vocabulary, total_user_words)
    bot_shannon_entropy = shannon_entropy(bot_vocabulary, total_bot_words)

    '''
        Conditional Shannon Entropy 
    '''

    cond_entrop = cond_entropy(bigrams, vocabulary, total_words)
    cond_user_entrop = cond_entropy(
        user_bigrams, user_vocabulary, total_user_words)
    cond_bot_entrop = cond_entropy(
        bot_bigrams, bot_vocabulary, total_bot_words)

    print("Total number of dialogs: " + str(dialog_count))
    print("Total number of turns: " + str(total_turns))
    print("Total number of user turns: " + str(total_user_turns))
    print("Total number of user words: " + str(total_user_words))
    print("Total number of bot words: " + str(total_bot_words))

    print()
    print("The mean of the number of turns per dialog: " +
          str(turns_mean))
    print("The mean of the number of user turns per dialog: " +
          str(user_turns_mean))
    print("The mean of the number of bot turns per dialog: " +
          str(bot_turns_mean))
    print("The standard deviation of the number of turns per dialog: " +
          str(turns_std))
    print("The standard deviation of the number of user turns per dialog: " +
          str(user_turns_std))
    print("The standard deviation of the number of bot turns per dialog: " +
          str(bot_turns_std))

    print()

    print("The mean of the number of words in turn: " +
          str(words_mean))
    print("The mean of the number of user words in turn: " +
          str(user_words_mean))
    print("The mean of the number of bot words in turn: " +
          str(bot_words_mean))
    print("The standard deviation of the number of words in turn: " +
          str(words_std))
    print("The standard deviation of the number of user words in turn: " +
          str(user_words_std))
    print("The standard deviation of the number of bot words in turn: " +
          str(bot_words_std))

    print()

    print("Total vocabulary size: " +
          str(len(vocabulary.keys())))
    print("User vocabulary size: " +
          str(len(user_vocabulary.keys())))
    print("Bot vocabulary size: " +
          str(len(bot_vocabulary.keys())))

    print()

    print("Total Shannon Entropy: " + str(total_shannon_entropy))
    print("User Shannon Entropy: " + str(user_shannon_entropy))
    print("Bot Shannon Entropy: " + str(bot_shannon_entropy))
    print("Total Conditional Shannon Entropy: " + str(cond_entrop))
    print("User Conditional Shannon Entropy: " + str(cond_user_entrop))
    print("Bot Conditional Shannon Entropy: " + str(cond_bot_entrop))


if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
