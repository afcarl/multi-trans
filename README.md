Automatic Construction of Multilingual Equivalents from Parallel Corpora

**Work In Progress**

Assume there are five paired sentences.
Lowercase letters represent words in language X (e.g., English), and capitals language Y (e.g., German). We want to find the best equivalent, or translation of `a`, which is A. (Ignore x and X, which represent some word)

a b c x x ; A B C X X
a b x x x ; B X X X X
a b x x x ; B X X X X
a c x x x ; C X X X X
a x x x x ; A X X X X

Orders are not important in this task.
The actual equivalents of a, b, and c are A, B, and C, respectively.
For example, we can think of `a`, `b`, and `c` as time, the, you.
`the` and `you` are extremely frequent in English, therefore they can act as confounds. 

===Notation
* S: translation score
* P: co-occurrence prob.

before adjustment:
S(a-A) = P(a-A) = 2/5
S(a-B) = P(a-B) = 3/5 <- Best
S(a-C) = P(a-C) = 2/5

after adjustment: we will take the co-occurrence prob. of `a`s collocates, which are tentative confounds into account.

S(a-A) = P(a-A) - [P(a-b)*P(b-A) + P(a-c)*P(c-A)]
			= 2/5 - (3/5 * 1/3 + 2/5 * 1/2)
			= 0 <- Best
S(a-B) = P(a-B) - [P(a-b)*P(b-B) + P(a-c)*P(c-B)]
			= 3/5 - (3/5 * 3/3 + 2/5 * 1/2]
			= -0.2
S(a-C) = P(a-C) - [P(a-b)*P(b-C) + P(a-c)*P(c-C)]
			= 2/5 - (3/5 * 1/3 + 2/5 * 2/2)
			= -0.2

