#!/usr/bin/env python3
# encoding: utf8


class TokenList(list):
    """
    A representation of utterances as list of tokens. Has all the regular list functions,
    plus a few more, useful for search and replacement.
    """

    def __init__(self, utt=None):
        if utt is None:
            super(TokenList, self).__init__()
        elif isinstance(utt, list):
            super(TokenList, self).__init__(utt)
        else:
            super(TokenList, self).__init__()
            self.extend(str(utt).strip().split())

    def any_word_in(self, words):
        words = words if not isinstance(words, str) else words.strip().split()
        for alt_expr in words:
            if alt_expr in self:
                return True
        return False

    def all_words_in(self, words):
        words = words if not isinstance(words, str) else words.strip().split()
        for alt_expr in words:
            if alt_expr not in self:
                return False
        return True

    def phrase_in(self, phrase):
        return self.phrase_pos(phrase) != -1

    def phrase_pos(self, phrase, start=0):
        """Returns the position of the given phrase in the given utterance, or -1 if not found.

        :rtype: int
        """
        phrase = phrase.strip().split() if not isinstance(phrase, list) else phrase
        # finding sub-list in a list (TODO optimize)
        for pos in range(start, len(self) - len(phrase) + 1):
            if self[pos:pos + len(phrase)] == phrase:
                return pos
        return -1

    def first_phrase_span(self, phrases):
        """Returns the span (start, end+1) of the first phrase from the given list
        that is found in the utterance. Returns (-1, -1) if no phrase is found.

        :param utterance: The utterance to search in
        :param phrases: a list of phrases to be tried (in the given order)
        :rtype: tuple
        """
        phrases = [phrase.strip().split() if not isinstance(phrase, list) else phrase
                   for phrase in phrases]
        for phrase in phrases:
            pos = self.phrase_pos(phrase)
            if pos != -1:
                return pos, pos + len(phrase)
        return -1, -1

    def any_phrase_in(self, phrases):
        return self.first_phrase_span(phrases) != (-1, -1)

    def ending_phrases_in(self, phrases):
        """Returns True if the utterance ends with one of the phrases

        :param phrases: a list of phrases to search for
        :rtype: bool
        """
        phrases = [phrase.strip().split() if not isinstance(phrase, list) else phrase
                   for phrase in phrases]

        for phrase in phrases:
            phr_pos = self.phrase_pos(phrase)
            if phr_pos > -1 and phr_pos + len(phrase) == len(self):
                return True
        return False

    def __eq__(self, other):
        if isinstance(other, list):
            return super(TokenList, self).__eq__(other)
        elif isinstance(other, str):
            return str(self) == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return ' '.join(self)

    def __repr__(self):
        return 'TokenList' + super(TokenList, self).__repr__()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return TokenList(super(TokenList, self).__getitem__(key))
        return super(TokenList, self).__getitem__(key)

    def __contains__(self, stuff):
        if isinstance(stuff, list):
            return self.phrase_in(phrase)
        else:
            return super(TokenList, self).__contains__(stuff)

    def replace(self, orig, repl):
        """
        Replace the first occurrence of orig with repl. Accepts both lists and strings
        as arguments (strings are converted to lists). Returns a newly created object with the result.
        """
        orig = orig.strip().split() if not isinstance(orig, list) else orig
        pos = self.phrase_pos(orig)
        if pos == -1:
            return TokenList(self)

        repl = repl.strip().split() if not isinstance(repl, list) else repl
        return TokenList(self[:pos] + repl + self[pos + len(orig):])

    def replace_all(self, orig, repl):
        """
        Replace all occurrences of orig with repl. Accepts both lists and strings
        as arguments (strings are converted to lists). Returns a newly created object with the result.
        """
        orig = orig.strip().split() if not isinstance(orig, list) else orig
        repl = repl.strip().split() if not isinstance(repl, list) else repl
        ret = TokenList()
        last_pos = 0
        pos = self.phrase_pos(orig)
        while pos != -1:
            ret.extend(self[last_pos:pos])
            ret.extend(repl)
            last_pos = pos + len(orig)
            pos = self.phrase_pos(orig, start=last_pos)
        ret.extend(self[last_pos:])
        return ret

