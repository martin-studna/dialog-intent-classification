#!/usr/bin/python3
import argparse
import sys
import re
import os

'''
    This script parses text from bAbi tasks data.
    Every line of bAbi data has user's and bot turn divided with tab symbol.
    The script generates output file, which formats user's and bot's turns in the following form:

    DIALOG 1:
    1. USER: ...
    2. BOT: ...
       ... 
'''


parser = argparse.ArgumentParser()

parser.add_argument(
    "--file", default="./dialog-babi-task6-dstc2-trn.txt", type=str, help="Input file.")


def main(args):

    if args.file == None:
        return

    output = os.path.basename(args.file).split(".")[0] + "-output.txt"

    if os.path.exists(output):
        os.remove(output)

    output = open(output, 'w')
    dialog = open(args.file)
    prevLine = None
    bot_utterance = ""
    user_utterance = None
    count = 1
    dialog_count = 0
    for line in dialog:
        if '\t' not in line:
            continue

        utterances = line.split('\t')

        prev_user_utterance = user_utterance
        user_utterance = utterances[0].split(' ', 1)[1]
        bot_utterance = utterances[1].rstrip()

        if utterances[0].split(' ', 1)[0] == '1':
            count = 1
            dialog_count += 1
            output.write("\n\nDIALOG NUMBER " + str(dialog_count))
            prev_user_utterance = None

        if "<SILENCE>" == user_utterance and prev_user_utterance is None:
            output.write("\n" + str(count) + ' ' + 'BOT: ' + bot_utterance)
            count += 1
        elif "<SILENCE>" == user_utterance:
            output.write(" " + utterances[1].rstrip())
        else:
            if user_utterance != '':
                output.write("\n" + str(count) + ' ' +
                             'USER: ' + user_utterance)
                count += 1
            output.write("\n" + str(count) + ' ' + 'BOT: ' + bot_utterance)
            count += 1

    dialog.close()
    output.close()


if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
