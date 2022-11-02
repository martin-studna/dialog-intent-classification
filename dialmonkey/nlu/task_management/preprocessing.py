#!/usr/bin/python3

from collections import defaultdict


# _NUMBERS = {0: 'nula', 1: 'jeden', 2: 'dva', 3: 'tři', 4: 'čtyři', 5: 'pět',
#             6: 'šest', 7: 'sedm', 8: 'osm', 9: 'devět', 10: 'deset',
#             11: 'jedenáct', 12: 'dvanáct', 13: 'třináct', 14: 'čtrnáct',
#             15: 'patnáct', 16: 'šestnáct', 17: 'sedmnáct', 18: 'osmnáct',
#             19: 'devatenáct', 20: 'dvacet', 30: 'třicet', 40: 'čtyřicet',
#             50: 'padesát', 60: 'šedesát', 70: 'sedmdesát', 80: 'osmdesát',
#             90: 'devadesát', 100: 'sto', 200: 'dvě stě', 300: 'tři sta',
#             400: 'čtyři sta', 500: 'pět set', 600: 'šest set', 700: 'sedm set',
#             800: 'osm set', 900: 'devět set', 1000: 'tisíc', 1100: 'jedenáct set',
#             1200: 'dvanáct set', 1300: 'třináct set', 1400: 'čtrnáct set',
#             1500: 'patnáct set', 1600: 'šestnáct set', 1700: 'sedmnáct set',
#             1800: 'osmnáct set', 1900: 'devatenáct set', 2000: 'dva tisíce',
#             3000: 'tři tisíce', 4000: 'čtyři tisíce', 5000: 'pět tisíc',
#             6000: 'šest tisíc', 7000: 'sedm tisíc', 8000: 'osm tisíc', 9000: 'devět tisíc'}


class Preprocessing(object):
    """Implements preprocessing of utterances or utterances and dialogue acts.
    The main purpose is to replace all values in the database by their category
    labels (slot names) to reduce the complexity of the input utterances.

    In addition, it implements text normalisation for SLU input, e.g. removing
    filler words such as UHM, UM etc., converting "I'm" into "I am" etc.  Some
    normalisation is hard-coded. However, it can be updated by providing
    normalisation patterns.

    """
    text_normalization_mapping = [
        (['erm'], ['']),
        (['uhm'], ['']),
        (['um'], ['']),
        ("i'm", ['i', 'am']),
        (['(sil)'], ['']),
        (['(%hesitation)'], ['']),
        (['(hesitation)'], ['']),
        (['_noise_'], ['']),
        (['_laugh_'], ['']),
        (['_ehm_hmm_'], ['']),
        (['_inhale_'], ['']),
        (['ve'], ['v']),
        (['ke'], ['k']),
        (['ku'], ['k']),
        (['ze'], ['z']),
        # (['se'], ['s']), # do not use this, FJ
        (['barandov'], ['barrandov']),
        (['litňanská'], ['letňanská']),
        (['ípé', 'pa', 'pavlova'], ['i', 'p', 'pavlova']),
        (['í', 'pé', 'pa', 'pavlova'], ['i', 'p', 'pavlova']),
        (['čaplinovo'], ['chaplinovo']),
        (['čaplinova'], ['chaplinova']),
        (['zologická'], ['zoologická']),
    ]

    def __init__(self, text_normalization=None):
        """Initialises a SLUPreprocessing object with particular preprocessing
        parameters.

        Arguments:
            cldb -- an iterable of (surface, value, slot) tuples describing the
                    relation between surface forms and (slot, value) pairs
            text_normalization -- an iterable of tuples (source, target) where
                    `source' occurrences in the text should be substituted by
                    `target', both `source' and `target' being specified as
                    a sequence of words

        """
        # self.cldb = cldb
        # num_norms = []
        # for num in range(60):
        #     num_norms.append(([str(num)], [word_for_number(num, 'F1')]))
        # self.text_normalization_mapping += num_norms

        if text_normalization:
            self.text_normalization_mapping = text_normalization

    def normalize(self, utterance):
        """
        Normalises the utterance (the output of an ASR) and returns it as a list of words/tokens.

        E.g., it removes filler words such as UHM, UM, etc., converts "I'm"
        into "I am", etc.
        """
        for mapping in self.text_normalization_mapping:
            utterance = utterance.replace_all(mapping[0], mapping[1])
        return utterance
