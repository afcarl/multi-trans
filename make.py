#-*- coding: utf-8 -*-
#!/usr/bin/python2

'''
Glossary"
 translation sentence: e.g., "I love you", "Ich liebe Dich"
 wx: A string. Word of source language X
 wy: A string. Word of target language Y
 x: An int. Encoded word of language X
 y: An int. Encoded word of language Y
 collocation: A phenomena that two words occur together.
 collocate of x: A word that occurs with x. Can exist in the same
    sentence as x, or in the translation sentence of x.
    the same language as x or not. Here represented as x2.
    E.g., the collocates of `love` in the above example are
        `I`, `you`, `Ich`, `liebe`, and `Dich`.
 collocation prob. of y on x: p(y|x) = cnt(x and y)/cnt(x)
 translation of (w)x: An equivalent of (w)x.
    e.g., Translation of "love" is "liebe".
 translation score of y on x: p(y|x) - sum(p(x2s|x)*p(y2s|x2s))
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

# # arguments setting
# parser = argparse.ArgumentParser()
# parser.add_argument('--l1', help="""ISO 639-1 code of target language. \n
#                                      'See `http://opus.lingfil.uu.se/OpenSubtitles2016.php`""")
# parser.add_argument('--l2', help="""ISO 639-1 code of target language. \n
#                                      'See `http://opus.lingfil.uu.se/OpenSubtitles2016.php`""")
# parser.add_argument('--n', help="number of lines that are used", default=30000000)
# parser.add_argument('--m', help="rate of word counts that count as lexicon", default=.8)
# parser.add_argument('--o', help="number of words that are used in calculating collocation", default=1000)
# parser.add_argument('--p', help="number of line that used as initial contstructor", default=100000)
# args = parser.parse_args()
#
# lcode1 = args.l1.lower()
# lcode2 = args.l2.lower()
# n = args.n
# m = args.m
# o = args.o
# p = args.p

# import re
# fs = set([re.search("[a-z]+\-[a-z]+", f).group() for f in glob.glob("data/*")])
# fs = fs - {"bn-en"}
# fs = fs - {"en-no"}
# fs = fs - {"en-eo"}
# fs = fs - {"en-nl"}
# fs = fs - {"en-sv"}
# fs = fs - {"en-hu"}
# fs = fs - {"en-it"}
# fs = fs - {"en-hi"}
# fs = fs - {"en-ms"}
# fs = fs - {"en-ru"}
# fs = fs - {"ca-en"}
# for f in fs:
# lcode1, lcode2 = f.split("-")
lcode1, lcode2 = "en", "nl"
# lcode1, lcode2 = sorted([lcode1, lcode2])
print("==========", lcode1, lcode2)

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

print("Step0. Normalize sentences")
print("\t## lcode1 ...")
sents1 = [word_segment(normalize(line, lcode1), lcode1)
            for line in tqdm(
                    codecs.open('data/OpenSubtitles2016.{}-{}.{}'.format(lcode1, lcode2, lcode1),
                    'r', 'utf-8').read().split("\n")[:300000000])]
print("\t## lcode2 ...")
sents2 = [word_segment(normalize(line, lcode2), lcode2)
          for line in tqdm(
        codecs.open('data/OpenSubtitles2016.{}-{}.{}'.format(lcode1, lcode2, lcode2),
                    'r', 'utf-8').read().split("\n"))]

assert len(sents1)==len(sents2), \
    """{} and {} MUST be the same in length.\n
       {} has {} lines, but {} has {} lines""".format(lcode1, lcode2,
                                                      lcode1, len(sents1),
                                                      lcode2, len(sents2))
# Create folder
if not os.path.exists('outputs/{}-{}'.format(lcode1, lcode2)): os.makedirs('outputs/{}-{}'.format(lcode1, lcode2))

print("Step1. Initialize dictionaries")
# conversion dictionaries
print("\t## lcode1...")
wx_to_x, x_to_wx, x_to_cnt = dict(), dict(), dict()
wx_to_cnt = Counter(tqdm(list(chain.from_iterable(sents1))))
for x, (wx, cnt) in enumerate(wx_to_cnt.most_common(len(wx_to_cnt))): # sorting is useful.
    if x > .8*len(wx_to_cnt): break
    wx_to_x[wx] = x
    x_to_wx[x] = wx
    x_to_cnt[x] = cnt

print("\t## lcode2...")
wy_to_y, y_to_wy, y_to_cnt = dict(), dict(), dict()
wy_to_cnt = Counter(tqdm(list(chain.from_iterable(sents2))))
for y, (wy, cnt) in enumerate(wy_to_cnt.most_common(len(wy_to_cnt))):
    if y > .8*len(wy_to_cnt): break
    wy_to_y[wy] = y
    y_to_wy[y] = wy
    y_to_cnt[y] = cnt

# collocation dictionaries
x_to_x2s = dict() # x2s: collocates of x. {x: {x2: cnt, x2: cnt, ...}}
y_to_y2s = dict() # y2s: collocates of y. {y: {y2: cnt, y2: cnt, ...}}

# translation dictionaries
x_to_ys = dict() # {x: {y: cnt, y: cnt, ...}}
y_to_xs = dict() # {y: {x: cnt, x: cnt, ...}}

print("Step2. Update dictionaries ...")
line_num = 1
for sent1, sent2 in tqdm(zip(sents1, sents2)):
    if len(sent1) <= 1 or len(sent2) <= 1: continue

    # To indices
    xs = [wx_to_x[wx] for wx in sent1 if wx in wx_to_x]
    ys = [wy_to_y[wy] for wy in sent2 if wy in wy_to_y]

    # Collocation dictionary updates
    def _update(xs, x_to_x2s):
        for x in xs:
            for x2 in xs:  # x2: collocate
                if x == x2: continue
                if x2 > 1000: continue  # Cut off infrequent words to save memory
                if x not in x_to_x2s: x_to_x2s[x] = dict()
                if x2 not in x_to_x2s[x]: x_to_x2s[x][x2] = 0
                x_to_x2s[x][x2] += 1

    ## lcode1
    _update(xs, x_to_x2s)
    ## lcode2
    _update(ys, y_to_y2s)

    # Translation dictionary updates
    for x in xs:
        for y in ys:
            if line_num <= 100000:
                ## lcode1 -> lcode2
                if x not in x_to_ys: x_to_ys[x] = dict()
                if y not in x_to_ys[x]: x_to_ys[x][y] = 0
                x_to_ys[x][y] += 1

                ## lcode1 <- lcode2
                if y not in y_to_xs: y_to_xs[y] = dict()
                if x not in y_to_xs[y]: y_to_xs[y][x] = 0
                y_to_xs[y][x] += 1
            else: # We don't add new words after some point to save memory.
                ## lcode1 -> lcode2
                if x in x_to_ys and \
                   y in x_to_ys[x] and \
                   x_to_ys[x][y] > 1: x_to_ys[x][y] += 1

                ## lcode1 <- lcode2
                if y in y_to_xs and \
                   x in y_to_xs[y] and \
                   y_to_xs[y][x] > 1: y_to_xs[y][x] += 1

    line_num += 1

print("# Adjust ...")
def _get_trans(x_to_ys, x_to_cnt, x_to_x2s):
    x_to_trans = dict()
    for x, ys in tqdm(x_to_ys.items()):
        if x not in x_to_x2s: continue # if there's no collocate, we don't have to adjust the score.
        cntx = x_to_cnt[x]
        y_scores = []
        for y, cnty in sorted(ys.items(), key=operator.itemgetter(1), reverse=True)[:20]:  # 20: heuristic
            ts = cnty / float(cntx)  # translation score: initial value
            for x2, cntx2 in x_to_x2s[x].items():  # Collocates
                p_x_x2 = cntx2 / float(cntx)
                p_x2_y2 = 0
                if x2 in x_to_ys:
                    p_x2_y2 = x_to_ys[x2].get(y, 0) / float(x_to_cnt[x2])
                ts -= (p_x_x2 * p_x2_y2)
            y_scores.append((y, ts))
        trans = sorted(y_scores, key=lambda x: x[1], reverse=True)[:10]  # 10: heuristic
        trans = [each[0] for each in trans]
        x_to_trans[x] = trans

    return x_to_trans

print("\t## lcode1 -> lcode2")
x_to_trans = _get_trans(x_to_ys, x_to_cnt, x_to_x2s)
print("\t## lcode1 <- lcode2")
y_to_trans = _get_trans(y_to_xs, y_to_cnt, y_to_y2s)

print("# sanity check")
def _sanity_check(wx_to_x, x_to_ys, x_to_trans, y_to_wy):
    if "time" not in wx_to_x: return ""
    time_id = wx_to_x["time"]

    # before adjustment
    ys = x_to_ys[time_id]
    y_cnt = sorted(ys.items(), key=operator.itemgetter(1), reverse=True)[:20]
    print("\tbefore adjustment the translations of `time` were =>", " | ".join(y_to_wy[y] for y, cnt in y_cnt))

    # after adjustment
    ys = x_to_trans[time_id]
    print("\tafter adjustment the translations of `time` are => ", " | ".join(y_to_wy[y] for y in ys))

if lcode1=="en": _sanity_check(wx_to_x, x_to_ys, x_to_trans, y_to_wy)
elif lcode2=="en": _sanity_check(wy_to_y, y_to_xs, y_to_trans, x_to_wx)

print("# Write")
## lexicons
pickle.dump((wx_to_x, x_to_wx), open('outputs/{}-{}/{}.lexicon.pkl'.format(lcode1, lcode2, lcode1), 'wb'))
pickle.dump((wy_to_y, y_to_wy), open('outputs/{}-{}/{}.lexicon.pkl'.format(lcode1, lcode2, lcode2), 'wb'))

## trans dictionary
pickle.dump(x_to_trans, open('outputs/{}-{}/{}-{}.trans.pkl'.format(lcode1, lcode2, lcode1, lcode2), 'wb'))
pickle.dump(y_to_trans, open('outputs/{}-{}/{}-{}.trans.pkl'.format(lcode1, lcode2, lcode2, lcode1), 'wb'))

print("Done!")