Automatic Construction of Multilingual Translation Word Pairs from Parallel Corpora

**Work In Progress**

* Glossary
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


Assume there are five English sentences and their counterparts in French. We want to find the translation of `apple` without using any external knowledge.

(a) the apple is mine
(b) I want the apple pie
(c) eat the apple
(d) an apple a day is good for health
(e) I like apple pies

(A) la pomme est à moi
(B) Je veux la tarte aux pommes
(C) manger la pomme
(D) une pomme par jour est bonne pour la santé
(E) J'aime les tartes aux pommes

The first approach is to calculate the collocation probability between apple and its all possible translations.

P(la|apple) = 4/5
P(pomme|apple) = 3/5
P(est|apple) = 2/5
...

`la` occurred four times out of five sentences where `apple` occurred. By constrast, `pomme` three time. So we can think `la` is likely to be the best translation of `apple` based on this calculation. But the correct translation of `apple` is actually `pomme`. `la` is a feminine definite article which is equivalent to `the`. Why did this happen?

It's because we didn't consider the fact that `apple` and `the` often occur together. (You know `the` is the most frequent word in English). Because of that, `la` can also often occur in French sentences containing `apple`. Therefore we should deduct the effect of `the` from the collocation prob. of the `apple-la` pair. Modified calcuations are as follows:

Score(la|apple) = P(la|apple) - (P(the|apple)*P(la|the) + P(is|apple)*P(la|is) + ...)
			= 4/5 - (3/5 * 3/3 + 2/5 * 2/2)
			= -0.19
Score(pomme|apple) = P(pomme|apple) - (P(the|apple)*P(pomme|the) + P(is|apple)*P(pomme|is) + ...)
			= 3/5 - (3/5 * 2/3 + 2/5 * 2/2)
			= -0.2

