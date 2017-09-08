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
        self.wx_to_x, self.x_to_wx = pickle.load(open('outputs/{}-{}/{}.lexicon.pkl'.format(a, b, source_lang), 'rb'))
        self.wy_to_y, self.y_to_wy = pickle.load(open('outputs/{}-{}/{}.lexicon.pkl'.format(a, b, target_lang), 'rb'))

        # Load trans dictionary
        self.x_to_ys = pickle.load(open('outputs/{}-{}/{}-{}.trans.pkl'.format(a, b, source_lang, target_lang), 'rb'))

    def __call__(self, query, top_k=3):
        if query not in self.wx_to_x:
            return "{} is not found in our database".format(query)
        elif self.wx_to_x[query] not in self.x_to_ys:
            return "Translation of {} is not found in our database".format(query)
        else:
            ys = self.x_to_ys[self.wx_to_x[query]][:top_k]
            trans = [self.y_to_wy[y] for y in ys]
            return trans