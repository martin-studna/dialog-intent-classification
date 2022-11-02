#!/usr/bin/python3

from collections import defaultdict


_NUMBERS = {0: 'nula', 1: 'jeden', 2: 'dva', 3: 'tři', 4: 'čtyři', 5: 'pět',
            6: 'šest', 7: 'sedm', 8: 'osm', 9: 'devět', 10: 'deset',
            11: 'jedenáct', 12: 'dvanáct', 13: 'třináct', 14: 'čtrnáct',
            15: 'patnáct', 16: 'šestnáct', 17: 'sedmnáct', 18: 'osmnáct',
            19: 'devatenáct', 20: 'dvacet', 30: 'třicet', 40: 'čtyřicet',
            50: 'padesát', 60: 'šedesát', 70: 'sedmdesát', 80: 'osmdesát',
            90: 'devadesát', 100: 'sto', 200: 'dvě stě', 300: 'tři sta',
            400: 'čtyři sta', 500: 'pět set', 600: 'šest set', 700: 'sedm set',
            800: 'osm set', 900: 'devět set', 1000: 'tisíc', 1100: 'jedenáct set',
            1200: 'dvanáct set', 1300: 'třináct set', 1400: 'čtrnáct set',
            1500: 'patnáct set', 1600: 'šestnáct set', 1700: 'sedmnáct set',
            1800: 'osmnáct set', 1900: 'devatenáct set', 2000: 'dva tisíce',
            3000: 'tři tisíce', 4000: 'čtyři tisíce', 5000: 'pět tisíc',
            6000: 'šest tisíc', 7000: 'sedm tisíc', 8000: 'osm tisíc', 9000: 'devět tisíc'}


_FORMS = {'jeden': {'jeden': ['M1', 'I1', 'M5', 'I5', 'I4'],
                    'jedna': ['F1', 'F5'],
                    'jedné': ['F2', 'F3', 'F6'],
                    'jedním': ['M7', 'I7', 'N7'],
                    'jednoho': ['M4', 'M2', 'I2', 'N2'],
                    'jednom': ['M6', 'I6', 'N6'],
                    'jednomu': ['M3', 'I3', 'N3'],
                    'jedno': ['N1', 'N4', 'N5'],
                    'jednou': ['F7'],
                    'jednu': ['F4']},
          'dva': {'dva': ['M1', 'M4', 'I1', 'I4', 'I5', 'M5'],
                  'dvěma': ['M7', 'I7', 'N7', 'F7', 'M3', 'I3', 'F3', 'N3'],
                  'dvě': ['F1', 'F4', 'F5', 'N1', 'N4', 'N5'],
                  'dvou': ['M2', 'I2', 'N2', 'F2', 'M6', 'I6', 'N6', 'F6']},
          'tři': {'tři': ['1', '4', '5'],
                  'tří': ['2'],
                  'třemi': ['7'],
                  'třem': ['3'],
                  'třech': ['6']},
          'čtyři': {'čtyři': ['1', '4', '5'],
                    'čtyř': ['2'],
                    'čtyřem': ['3'],
                    'čtyřech': ['6'],
                    'čtyřmi': ['7']},
          'sto': {'sto': ['1', '4', '5'],
                  'sta': ['2'],
                  'stu': ['3', '6'],
                  'stem': ['7']},
          'tisíc': {'tisíc': ['1', '4', '5'],
                    'tisíce': ['2'],
                    'tisíci': ['3', '6'],
                    'tisícem': ['7']}}

# inverted _FORMS
_INFLECT = {}
for num, forms in _FORMS.items():
    _INFLECT[num] = {}
    for form, categs in forms.items():
        for categ in categs:
            _INFLECT[num][categ] = form


def word_for_number(number, categ='M1'):
    """\
    Returns a word given a number 1-100 (in the given gender + case).
    Gender (M, I, F, N) and case (1-7) are given concatenated.
    """
    # > 2000: composed of thousands and the rest (1000-2000 are composed of hunderds)
    if number > 2000 and number % 1000 != 0:
        return ' '.join((word_for_number((number // 1000) * 1000, categ),
                         word_for_number(number % 1000, categ)))
    # > 100: composed of hunderds and the rest
    if number > 100 and number % 100 != 0:
        return ' '.join((word_for_number((number // 100) * 100, categ),
                         word_for_number(number % 100, categ)))
    # > 20: composed of tens and ones
    if number > 20 and number % 10 != 0:
        # 21, 31... - "1" has no declension
        if number % 10 == 1:
            return ' '.join((word_for_number((number // 10) * 10, categ),
                             'jedna'))
        # 22, 32... - "2" doesn't change for different genders (set to masc.)
        if number % 10 == 2:
            categ = 'M' + categ if len(categ) == 1 else 'M' + categ[1]
        # other numbers are OK
        return ' '.join((word_for_number((number // 10) * 10, categ),
                         word_for_number(number % 10, categ)))
    # 0 = no declension
    if number == 0:
        return _NUMBERS[0]
    if number > 2 and len(categ) > 1:
        categ = categ[1]
    if number <= 4:
        return _INFLECT[_NUMBERS[number]][categ]
    num_word = _NUMBERS[number]
    if categ in ['2', '3', '6', '7']:
        if number == 9:
            num_word = num_word[:-2] + 'íti'
        else:
            num_word += 'i'
    return num_word


class CategoryLabelDatabase(object):
    """Provides a convenient interface to a database of slot value pairs aka
    category labels.

    Attributes:
        synonym_value_category: a list of (form, value, category label) tuples

    Mapping surface forms to category labels
    ----------------------------------------

    In an utterance:

    - there can be multiple surface forms in an utterance
    - surface forms can overlap
    - a surface form can map to multiple category labels

    Then when detecting surface forms / category labels in an utterance:

    #. find all existing surface forms / category labels and generate a new utterance with for every found surface form and
       category label (called abstracted), where the original surface form is replaced by its category label

       - instead of testing all surface forms from the CLDB from the longest to the shortest in the utterance, we test
         all the substrings in the utterance from the longest to the shortest


    """
    def __init__(self, db):
        self.database = {}
        self.synonym_value_category = []
        self.forms = []
        self.form_value_cl = []
        self.form2value2cl = {}

        self.load(db)

        # Bookkeeping.
        self._form_val_upname = None
        self._form_upnames_vals = None

    def __iter__(self):
        """Yields tuples (form, value, category) from the database."""
        for tup in self.synonym_value_category:
            yield tup

    @property
    def form_val_upname(self):
        """list of tuples (form, value, name.upper()) from the database"""
        if self._form_val_upname is None:
            self._form_val_upname = [(form, val, name.upper()) for (form, val, name) in self]
        return self._form_val_upname

    @property
    def form_upnames_vals(self):
        """list of tuples (form, upnames_vals) from the database
        where upnames_vals is a dictionary
            {name.upper(): all values for this (form, name)}.

        """
        if self._form_upnames_vals is None:
            # Construct the mapping surface -> category -> [values],
            # capturing homonyms within their category.
            upnames_vals4form = defaultdict(lambda: defaultdict(list))
            for form, val, upname in self.form_val_upname:
                upnames_vals4form[form][upname].append(val)
            self._form_upnames_vals = \
                [(form, dict(upnames_vals))
                 for (form, upnames_vals) in
                 sorted(upnames_vals4form.viewitems(), key=lambda item:-len(item[0]))]
        return self._form_upnames_vals

    def load(self, db):
        self.database = db
        self.normalise_database()
        # Update derived data structures.
        self.gen_synonym_value_category()
        self.gen_form_value_cl_list()
        self.gen_mapping_form2value2cl()

        self._form_val_upname = None
        self._form_upnames_vals = None

    def normalise_database(self):
        """Normalise database. E.g., split utterances into sequences of words.
        """
        new_db = dict()
        for name in self.database:
            new_db[name] = dict()
            for value in self.database[name]:
                new_db[name][value] = [tuple(form.split()) for form in self.database[name][value]]
        self.database = new_db

    def gen_synonym_value_category(self):
        for name in self.database:
            for value in self.database[name]:
                for form in self.database[name][value]:
                    self.synonym_value_category.append((form, value, name))
        # Sort the triples from those with most words to those with fewer
        # words.
        self.synonym_value_category.sort(
            key=lambda svc: len(svc[0]), reverse=True)

    def gen_form_value_cl_list(self):
        """
        Generates an list of form, value, category label tuples from the database. This list is ordered where the tuples
        with the longest surface forms are at the beginning of the list.

        :return: none
        """
        for cl in self.database:
            for value in self.database[cl]:
                for form in self.database[cl][value]:
                    self.form_value_cl.append((form, value, cl))

        self.form_value_cl.sort(key=lambda fvc: len(fvc[0]), reverse=True)

    def gen_mapping_form2value2cl(self):
        """
        Generates a form -> value -> category labels mapping from the database and
        stores it in self.form2value2cl.

        :return: none
        """
        for cl in self.database:
            for value in self.database[cl]:
                for form in self.database[cl][value]:
                    self.form2value2cl[form] = self.form2value2cl.get(form, {})
                    self.form2value2cl[form][value] = self.form2value2cl[form].get(value, [])
                    self.form2value2cl[form][value].append(cl)


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

    def __init__(self, cldb, text_normalization=None):
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
        self.cldb = cldb
        num_norms = []
        for num in range(60):
            num_norms.append(([str(num)], [word_for_number(num, 'F1')]))
        self.text_normalization_mapping += num_norms

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
