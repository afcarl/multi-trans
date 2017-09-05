#-*- coding: utf-8 -*-
#!/usr/bin/python2

from __future__ import print_function
import os
import pickle
# from make import *

class Trans:

    def __init__(self, source_lang="en", target_lang="de"):
        self.source_lang = source_lang
        self.target_lang = target_lang

        a, b = sorted([self.source_lang, self.target_lang])

        # Load lexicon
        self.word1_to_idx, self.idx_to_word1 = pickle.load(open('dict/{}-{}/{}.lexicon.pkl'.format(a, b, source_lang), 'rb'))
        self.word2_to_idx, self.idx_to_word2 = pickle.load(open('dict/{}-{}/{}.lexicon.pkl'.format(a, b, target_lang), 'rb'))

        # Load trans dictionary
        self.idx1_to_trans = pickle.load(open('dict/{}-{}/{}-{}.trans.pkl'.format(a, b, source_lang, target_lang), 'rb'))

    def __call__(self, query, show_freq=True, show_trans_freq=True, top_k=10):
        if query not in self.word1_to_idx:
            return "{} is not found in our database".format(query)
        elif self.word1_to_idx[query] not in self.idx1_to_trans:
            return "Translation of {} is not found in our database".format(query)
        else:
            freq, trans = self.idx1_to_trans[self.word1_to_idx[query]]
            if show_trans_freq:
                trans = [(self.idx_to_word2[idx], f) for idx, f in trans][:top_k]
            else:
                trans = [self.idx_to_word2[idx] for idx, f in trans][:top_k]

            if show_freq:
                return freq, trans
            else:
                return trans