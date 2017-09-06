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
        self.word1_to_idx1, self.idx1_to_word1 = pickle.load(open('outputs/{}-{}/{}.lexicon.pkl'.format(a, b, source_lang), 'rb'))
        self.word2_to_idx2, self.idx2_to_word2 = pickle.load(open('outputs/{}-{}/{}.lexicon.pkl'.format(a, b, target_lang), 'rb'))

        # Load trans dictionary
        self.idx1_to_idx2s = pickle.load(open('outputs/{}-{}/{}-{}.trans.pkl'.format(a, b, source_lang, target_lang), 'rb'))

    def __call__(self, query, top_k=3):
            return "{} is not found in our database".format(query)
        elif self.word1_to_idx1[query] not in self.idx1_to_idx2s:
            return "Translation of {} is not found in our database".format(query)
        else:
            idx2s = self.idx1_to_idx2s[self.word1_to_idx1[query]][:top_k]
            trans = [self.idx2_to_word2[idx2] for idx2 in idx2s]
            return trans