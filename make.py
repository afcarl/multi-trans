#-*- coding: utf-8 -*-
#!/usr/bin/python2

'''
Glossary"
 paired sentences: e.g., "I love you", "Ich liebe Dich"
 wx: A string. word of source language
 wy: A string. word of target language
 x: An int. encoded word of source language
 y: An int. encoded word of target language
 collocation: Occurrence of a word in the same sentence.
    e.g., "love" and "you" or "Ich" and "Dich"
 collocate of (w)x: A word that occurs in the same sentence as x.
    e.g., collocates of "love" are "I" and "you".
 cooccurrence: (occurrence of) a word in the paired sentence.
    e.g., cooccurrences of "love" are "Ich", "liebe", and "Dich".
 collocation score of x' on x: #(x and x') / #x
 cooccurrence score of y on x: #(x and y) / #x
 translation of (w)x: An equivalent of (w)x.
    e.g., Translation of "love" is "liebe".
 translation score of y on x:
    cooccurrence score - sum of (collocation score*cooccurrence score for every collocate)
kyubyong. http://www.github.com/Kyubyong/py-trans
'''
from __future__ import print_function
import codecs
import os
import regex
import pickle
import operator
import glob
from collections import Counter
from itertools import chain
from tqdm import tqdm
import argparse

# arguments setting
parser = argparse.ArgumentParser()
parser.add_argument('--l1', help="""ISO 639-1 code of target language. \n
                                     'See `http://opus.lingfil.uu.se/OpenSubtitles2016.php`""")
parser.add_argument('--l2', help="""ISO 639-1 code of target language. \n
                                     'See `http://opus.lingfil.uu.se/OpenSubtitles2016.php`""")
args = parser.parse_args()

lcode1 = args.l1.lower()
lcode2 = args.l2.lower()

# Special tokenizers
if "ko" in (lcode1, lcode2):
    from konlpy.tag import Kkma  # pip install konlpy. See http://konlpy.org/en/v0.4.4/ for further information.
    kkma = Kkma()
elif "ja" in (lcode1, lcode2):
    import MeCab  # See https://pypi.python.org/pypi/mecab-python/0.996
    mecab = MeCab.Tagger("-Owakati")
elif "zh" in (lcode1, lcode2):
    import jieba
elif "vi" in (lcode1, lcode2):
    from pyvi.pyvi import ViTokenizer
elif "th" in (lcode1, lcode2):
    import pythai

def normalize(text, lcode):
    if lcode in ['ko']:  # korean
        text = regex.sub(u"[^ \p{Hangul}]", " ", text)  # Replace unacceptable characters with a space.
    elif lcode in ['ja']:  # japanese
        text = regex.sub(u"[^\p{Han}\p{Hiragana}\p{Katakana}ー]", "", text)
    elif lcode in ['zh']:  # chinsese
        text = regex.sub(u"[^\p{Han}]", "", text)
    elif lcode in ['th']:  # thai
        text = regex.sub(u"[^ \p{Thai}]", " ", text)
    elif lcode in ['ru']:  # russian
        text = regex.sub(u"[^ \p{Cyrillic}\-]", " ", text)
        text = text.lower()
    # elif lcode in ['ar']: # arabic
    #         text = regex.sub(u"[^ \p{Arabic}.?!\-]", " ", text)
    elif lcode in ['hi']:  # hindi
        text = regex.sub(u"[^ \p{Devanagari}\-]", " ", text)
    elif lcode in ['bn']:  # bengali
        text = regex.sub(u"[^ \p{Bengali}\-]", " ", text)
    elif lcode in ['de']:  # german
        text = regex.sub(u"[^ \p{Latin}\-']", " ", text)
    else:  # Mostly european languages
        text = regex.sub(u"[^ \p{Latin}\-']", " ", text)
        text = text.lower()

    # Common
    text = regex.sub("[ ]{2,}", " ", text)  # Squeeze spaces.
    return text

def word_segment(sent, lcode):
    if lcode in ['ko']:
        words = [word for word, _ in kkma.pos(sent)]
    # elif lcode in ['ja']:
    #     words = mecab.parse(sent.encode('utf8')).split()
    # elif lcode in ['th']:
    #     words = pythai.split(sent)
    elif lcode in ['vi']:
        words = ViTokenizer.tokenize(sent).split()
    elif lcode in ['zh']:
        words = list(jieba.cut(sent, cut_all=False))
    else:  # Mostly european languages
        words = sent.split()

    return words

print("# get normalized sents")
a, b = sorted([lcode1, lcode2])

def _get_sents(lcode):
    sents = []
    for line in tqdm(codecs.open('data/OpenSubtitles2016.{}-{}.{}'.format(a, b, lcode), 'r', 'utf-8').read().split("\n")):
        sent = normalize(line, lcode)
        sent = word_segment(sent, lcode)
        sents.append(sent)
    return sents

print("## making sentences of lcode1 ...")
sents1 = _get_sents(lcode1)
print("## making sentences of lcode2 ...")
sents2 = _get_sents(lcode2)

assert len(sents1)==len(sents2), \
    """{} and {} MUST be the same in length.\n
       {} has {} lines, but {} has {} lines""".format(lcode1, lcode2,
                                                      lcode1, len(sents1),
                                                      lcode2, len(sents2))
print("# Make folder")
if not os.path.exists('outputs/{}-{}'.format(a, b)): os.makedirs('outputs/{}-{}'.format(a, b))

print("# Initialize dictionaries")
# conversion dictionaries
wx_to_x, x_to_wx, x_to_cnt = dict(), dict(), dict()
wx_to_cnt = Counter(list(chain.from_iterable(sents1)))
for x, (wx, cnt) in enumerate(wx_to_cnt.most_common(len(wx_to_cnt))): # sorting is useful.
    wx_to_x[wx] = x
    x_to_wx[x] = wx
    x_to_cnt[x] = cnt

wy_to_y, y_to_wy, y_to_cnt = dict(), dict(), dict()
wy_to_cnt = Counter(list(chain.from_iterable(sents2)))
for y, (wy, cnt) in enumerate(wy_to_cnt.items()):
    wy_to_y[wy] = y
    y_to_wy[y] = wy
    y_to_cnt[y] = cnt

# For sanity check
time_id = wx_to_x['time']

# collocation dictionaries
x_to_x2s = dict() # x2s: collocates of x. {x: {x2: cnt, x2: cnt, ...}}
y_to_y2s = dict() # y2s: collocates of y. {y: {y2: cnt, y2: cnt, ...}}

# translation dictionaries
x_to_ys = dict() # {x: {y: cnt, y: cnt, ...}}
y_to_xs = dict() # {y: {x: cnt, x: cnt, ...}}

print("# Update dictionaries ...")
for sent1, sent2 in tqdm(zip(sents1, sents2)):
    if len(sent1) <= 1 or len(sent2) <= 1: continue

    # To indices
    xs = [wx_to_x[wx] for wx in sent1]
    ys = [wy_to_y[wy] for wy in sent2]

    # Collocation dictionary updates
    ## lcode1 -> lcode2
    for x in xs:
        for x2 in xs: # x2: collocate
            if x==x2: continue
            if x2 > 1000: continue # Prune infrequent words
            if x not in x_to_x2s: x_to_x2s[x] = dict()
            if x2 not in x_to_x2s[x]: x_to_x2s[x][x2] = 0
            x_to_x2s[x][x2] += 1

    # lcode1 <- lcode2
    for y in ys:
        for y2 in ys:
            if y==y2: continue
            if y2 > 1000: continue
            if y not in y_to_y2s: y_to_y2s[y] = dict()
            if y2 not in y_to_y2s[y]: y_to_y2s[y][y2] = 0
            y_to_y2s[y][y2] += 1

    # Translation dictionary updates
    for x in xs:
        for y in ys:
            ## lcode1 -> lcode2
            if x not in x_to_ys: x_to_ys[x] = dict()
            if y not in x_to_ys[x]: x_to_ys[x][y] = 0
            x_to_ys[x][y] += 1

            ## lcode1 <- lcode2
            if y not in y_to_xs: y_to_xs[y] = dict()
            if x not in y_to_xs[y]: y_to_xs[y][x] = 0
            y_to_xs[y][x] += 1

print("# Adjust and fix final translations")
def _get_trans(x_to_ys, x_to_cnt, x_to_x2s):
    x_to_trans = dict()
    for x, ys in tqdm(x_to_ys.items()):
        cntx = x_to_cnt[x]
        y_scores = []
        if x == time_id: print("freq. of time =", cntx) # for sanity check

        for y, cnty in sorted(ys.items(), key=operator.itemgetter(1), reverse=True)[:20]:  # 20: heuristic
            translation_score = cnty / float(cntx)  # initial value
            # if x == time_id and x2 == the_id:
            #     print("\n\ntrans=", y_to_wy[y]);
            #     print("translation_score=", translation_score)
            try:
                for x2, cntx2 in x_to_x2s[x].items():  # Collocates
                    # if x == time_id and x2 == the_id:
                    #     print("collocate=", x_to_wx[x2])
                    collocation_score = cntx2 / float(cntx)
                    coocurrence_score = x_to_ys[x2].get(y, 0) / float(x_to_cnt[x2])
                    translation_score -= (collocation_score * coocurrence_score)
                    # if x == time_id and x2 == the_id:
                    #     print("collocation score=", collocation_score, cntx2)
                    #     print("coocurrence_score=", coocurrence_score, x_to_ys[x2].get(y, 0, ), float(x_to_cnt[x2]))
                    #     print("minus score=", collocation_score * coocurrence_score)
            except:
                continue
            # if x == time_id:
            #     print("\n=====\n", "finale translation score=", translation_score)
            y_scores.append((y, translation_score))
        trans = sorted(y_scores, key=lambda x: x[1], reverse=True)[:10]  # 10: heuristic
        trans = [each[0] for each in trans]
        x_to_trans[x] = trans
    return x_to_trans

print("## lcode1 -> lcode2")
x_to_trans = _get_trans(x_to_ys, x_to_cnt, x_to_x2s)
print("## lcode1 <- lcode2")
y_to_trans = _get_trans(y_to_xs, y_to_cnt, y_to_y2s)


print("# sanity check")
# before adjustment
ys = x_to_ys[time_id]
y_cnt = sorted(ys.items(), key=operator.itemgetter(1), reverse=True)[:20]
print("before adjustment the translations of `time` were =>", " | ".join(y_to_wy[y] for y, cnt in y_cnt))

# after adjustment
ys = x_to_trans[time_id]
print("after adjustment the translations of `time` are => ", " | ".join(y_to_wy[y] for y in ys))

print("# Write")
## lexicons
pickle.dump((wx_to_x, x_to_wx), open('outputs/{}-{}/{}.lexicon.pkl'.format(a, b, lcode1), 'wb'))
pickle.dump((wy_to_y, y_to_wy), open('outputs/{}-{}/{}.lexicon.pkl'.format(a, b, lcode2), 'wb'))

## trans dictionary
pickle.dump(x_to_trans, open('outputs/{}-{}/{}-{}.trans.pkl'.format(a, b, lcode1, lcode2), 'wb'))
pickle.dump(y_to_trans, open('outputs/{}-{}/{}-{}.trans.pkl'.format(a, b, lcode2, lcode1), 'wb'))

print("Done!")