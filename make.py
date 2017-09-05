#-*- coding: utf-8 -*-
#!/usr/bin/python2

from __future__ import print_function
import codecs
import os
import regex
import pickle
import operator
import glob
from collections import Counter
from itertools import chain

# Special tokenizers
from konlpy.tag import Kkma  # pip install konlpy. See http://konlpy.org/en/v0.4.4/ for further information.
kkma = Kkma()
# import MeCab  # See https://pypi.python.org/pypi/mecab-python/0.996
# mecab = MeCab.Tagger("-Owakati")
import jieba
from pyvi.pyvi import ViTokenizer
# import pythai

def get_stopwords(sents, n=100):
    words = list(chain.from_iterable(sents))
    word2cnt = Counter(words)
    top_words = [word for word, cnt in word2cnt.most_common(n)]
    return top_words

def normalize(text, lcode):
    if lcode in ['ko']:  # korean
        text = regex.sub(u"[^ \r\n\p{Hangul}]", " ", text)  # Replace unacceptable characters with a space.
    elif lcode in ['ja']:  # japanese
        text = regex.sub(u"[^\r\n\p{Han}\p{Hiragana}\p{Katakana}ー]", "", text)
    elif lcode in ['zh']:  # chinsese
        text = regex.sub(u"[^\r\n\p{Han}]", "", text)
    elif lcode in ['th']:  # thai
        text = regex.sub(u"[^ \r\n\p{Thai}]", " ", text)
    elif lcode in ['ru']:  # russian
        text = regex.sub(u"[^ \r\n\p{Cyrillic}\-]", " ", text)
        text = text.lower()
    # elif lcode in ['ar']: # arabic
    #         text = regex.sub(u"[^ \r\n\p{Arabic}.?!\-]", " ", text)
    elif lcode in ['hi']:  # hindi
        text = regex.sub(u"[^ \r\n\p{Devanagari}\-]", " ", text)
    elif lcode in ['bn']:  # bengali
        text = regex.sub(u"[^ \r\n\p{Bengali}\-]", " ", text)
    elif lcode in ['de']:  # german
        text = regex.sub(u"[^ \r\n\p{Latin}\-']", " ", text)
    else:  # Mostly european languages
        text = regex.sub(u"[^ \r\n\p{Latin}\-']", " ", text)
        text = text.lower()

    # Common
    text = regex.sub("[ ]{2,}", " ", text)  # Squeeze spaces.
    return text


def word_segment(sent, lcode):
    '''
    Args:
      sent: A string. A sentence.

    Returns:
      A list of words.
    '''
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

def make_sents(lcode1, lcode2, n=100):
    a, b = sorted([lcode1, lcode2])
    ret = []
    for lcode in (lcode1, lcode2):
        # print("Making sentence list of {} ...".format(lcode))
        sents = []
        text = codecs.open('data/OpenSubtitles2016.{}-{}.{}'.format(a, b, lcode), 'r', 'utf-8').read()

        for line in text.split("\n"):
            sent = normalize(line.strip(), lcode)
            words = word_segment(sent, lcode)
            sents.append(words)
        ret.append(sents)
    return ret


def make(sents1, sents2, lcode1, lcode2, n=100, top_k=10):
    if len(sents1)!=len(sents2):
        print(len(sents1), len(sents2))#"{} and {} must be the same in length".format(sents1, sents2)
        print(sents1[-10:])
        print(sents2[-10:])

    # Make folder
    a, b = sorted([lcode1, lcode2])
    if not os.path.exists('dict/{}-{}'.format(a, b)): os.makedirs('dict/{}-{}'.format(a, b))

    # Load lexicons
    if os.path.exists('dict/{}-{}/{}.lexicon.pkl'.format(a, b, lcode1)):
        word1_to_idx, idx_to_word1 = pickle.load(open('dict/{}-{}/{}.lexicon.pkl'.format(a, b, lcode1), 'rb'))
    else:
        word1_to_idx, idx_to_word1 = dict(), dict()

    if os.path.exists('lexicon/{}-{}/{}.lexicon.pkl'.format(a, b, lcode2)):
        word2_to_idx, idx_to_word2 = pickle.load(open('lexicon/{}-{}/{}.lexicon.pkl'.format(a, b, lcode2), 'rb'))
    else:
        word2_to_idx, idx_to_word2 = dict(), dict()

    # Trans dictionary
    idx1_to_trans = dict()

    # Get stop words
    free_words = get_stopwords(sents1, n)
    stop_words = get_stopwords(sents2, n)
    print(stop_words[:3])

    # Main job
    for sent1, sent2 in zip(sents1, sents2):
        if len(sent1) > 1 and len(sent2) > 1:
            for word1 in sent1:
                if word1 not in word1_to_idx:
                    word1_to_idx[word1], idx_to_word1[len(word1_to_idx)-1] = len(word1_to_idx), word1
                idx1 = word1_to_idx[word1]

                if idx1 not in idx1_to_trans:
                    idx1_to_trans[idx1] = [0, dict()]
                idx1_to_trans[idx1][0] += 1 # hw freq ++

                for word2 in sent2:
                    if (word1 not in free_words) and (word2 in stop_words): continue
                    if word2 not in word2_to_idx:
                        word2_to_idx[word2], idx_to_word2[len(word2_to_idx)-1]= len(word2_to_idx), word2
                    idx2 = word2_to_idx[word2]

                    if idx2 not in idx1_to_trans[idx1][1]:
                        idx1_to_trans[idx1][1][idx2] = 1
                    else:
                        idx1_to_trans[idx1][1][idx2] += 1 # trans freq ++

    # translation reverse sort
    trans_dict = dict()
    for idx1, trans in idx1_to_trans.items():
        freq, idx2cnt = trans
        idx_cnt = sorted(idx2cnt.items(), key=operator.itemgetter(1), reverse=True)
        idx_cnt = [(idx, cnt) for idx, cnt in idx_cnt][:top_k] # prune
        trans_dict[idx1] = [freq, idx_cnt]

    # Write
    ## lexicons
    pickle.dump((word1_to_idx, idx_to_word1), open('dict/{}-{}/{}.lexicon.pkl'.format(a, b, lcode1), 'wb'))
    pickle.dump((word2_to_idx, idx_to_word2), open('dict/{}-{}/{}.lexicon.pkl'.format(a, b, lcode2), 'wb'))

    ## trans dictionary
    pickle.dump(trans_dict, open('dict/{}-{}/{}-{}.trans.pkl'.format(a, b, lcode1, lcode2), 'wb'))

if __name__ == "__main__":
    fs = {regex.search("[a-z]+\-[a-z]+", f).group() for f in glob.glob('data/*')}
    for f in fs:
        lcode1, lcode2 = f.split("-")
        print(lcode1, lcode2)
        sents1, sents2 = make_sents(lcode1, lcode2)
        make(sents1, sents2, lcode1, lcode2)
        make(sents2, sents1, lcode2, lcode1)
        print("Done")
