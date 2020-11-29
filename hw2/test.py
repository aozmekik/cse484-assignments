import random
import re
from nltk import ngrams, trigrams
from collections import Counter, defaultdict
from sgt import SimpleGoodTuring
import numpy as np
import math

# TASKS.
# TODO. gt-smoothing.
# TODO. produce random sentences.
#


def read_file(file):
    X = []
    with open(file, 'r', encoding='utf-8', errors='ignore') as file:
        X = normalize(file.read()).split()
    return X


def normalize(X):
    # just lower case letters.
    return X.lower().strip()


def split(X, ratio=0.05):
    N = int(len(X) * (1-ratio))
    return X[:N], X[N:]


def get_sample(file, sample_name, N=20):
    '''
        Gets N sample randomly from given word list and write to the file.
        @param file, name of the file containing word list.
        @param sample_name, name of the new file containing N samples.
        @param N, sample count.
    '''
    X = read_file(file)
    print(int(len(X) * (N/100)))
    X = ' '.join([X[i] for i in range(int(len(X) * (N/100)))])
    # words = ' '.join([word for word in words])
    with open(sample_name, 'w', encoding='utf-8') as file:
        file.write(X)


# def smooth(M, words, n, wi=None):
#     Nc = defaultdict(lambda: 0)
#     N = 0
#     if n == 1:
#         # count all the counts
#         for w in M:
#             c = M[w]
#             Nc[c] += 1
#             N += c

#         # unigrams that never occured
#         # Nc[0] = len(words) - N
#         Nc[0] = 1  # FIXME.

#         for w in M:
#             c = M[w]
#             M[w] = (c + 1) * (Nc[c+1]/Nc[c])
#     else:
#         M_temp = defaultdict(lambda: 0)
#         # count all the counts
#         for wi in M:
#             for wj in M[wi]:
#                 c = M[wi][wj]
#                 Nc[c] += 1
#                 N += c
#                 M_temp[wi + (wj,)] = c

#         # ngrams that never occured
#         Nc[0] = len(words)**n - N
#         print(max(Nc))

#         M_temp, M_temp_keys = SimpleGoodTuring(M_temp, max(Nc)).run_sgt()
#         X = {}
#         for i, _ in enumerate(M_temp):
#             X[M_temp_keys[i]] = M_temp[i]

#         # apply good turing smoothing
#         for wi in M:
#             for wj in M[wi]:
#                 c = M[wi][wj]
#                 M[wi][wj] = X[c]
#             M[wi][-1] = Nc[1] / Nc[0]
#         M[-1][-1] = (Nc[1] / Nc[0]) / N
#         print(M[-1][-1])

#     # revised count for ngrams that never occured
#     # M[None] = Nc[1] / Nc[0]  # FIX

def gen_c(Nc, c):
    m = max(Nc.keys())
    if c > m:
        Nc[c] = m
    else:
        c_below = c
        while c_below not in Nc:
            c_below -= 1
        c_above = c
        while c_above not in Nc:
            c_above += 1
        Nc[c] = (Nc[c_above] + Nc[c_below]) / 2


def smooth(M, words, n, wi=None):
    Nc = defaultdict(lambda: 0)
    N = 0

    if n == 1:
        # count all the counts
        for w in M:
            c = M[w]
            Nc[c] += 1
            N += c

        # unigrams that never occured
        # Nc[0] = len(words) - N
        Nc[0] = 1  # FIXME.

        for w in M:
            c = M[w]
            if c not in Nc:
                gen_c(Nc, c)
            M[w] = (c + 1) * (Nc[c+1]/Nc[c])

    for wi in M:
        for wj in M[wi]:
            c = M[wi][wj]
            Nc[c] += 1
            N += c

    # ngrams that never occured
    Nc[0] = len(words)**n - N

    # apply good turing smoothing
    for wi in M:
        for wj in M[wi]:
            c = M[wi][wj]
            if c not in Nc:
                gen_c(Nc, c)
            if c + 1 not in Nc:
                gen_c(Nc, c + 1)
            M[wi][wj] = (c + 1) * (Nc[c+1]/Nc[c])
        M[wi][-1] = Nc[1] / Nc[0]
    M[-1][-1] = (Nc[1] / Nc[0]) / N


def model(words, n):
    if n == 1:
        # count
        counter = Counter(ngrams(words, 1))
        M = {word[0]: counter[word] for word in counter}

        # smooth
        smooth(M, words, n)

        # counts to probabilities
        total_count = float(sum(M.values()))
        for w in M:
            M[w] /= total_count
    else:
        # count
        M = defaultdict(lambda: defaultdict(lambda: 0))
        for w in ngrams(words, n, pad_right=True, pad_left=True):
            M[w[: n-1]][w[-1]] += 1

        # smooth
        smooth(M, words, n)
        # M_temp = smooth(M, words, n)

        # for w in M:
        #     M[w] /= M_count[w[: n-1]]
        # counts to probabilities
        for wi in M:
            if wi != -1:
                total_count = float(sum(M[wi].values()))
                for wj in M[wi]:
                    M[wi][wj] /= total_count
                M[wi][-1] /= total_count
    return M


def build_models(X):
    Ms = []
    for n in range(1, 6):
        Ms.append(model(X, n))
    return Ms


def test_models(Ms, Y):
    PPs = [PPs.append(Ms[0], Y, unigram=True)]
    for M in Ms[1:]:
        PPs.append(pp(M, Y))
    return PPs


def p(M, w1, w2):
    if not w2:  # unigram
        return M[w1] if M[w1] else M[None]
    if w1 in M:
        if w2 in M[w1]:
            X = M[w1][w2]
        else:
            X = M[w1][-1]
    else:
        X = M[-1][-1]
    return X


def pp(M, Y, unigram=False):
    x = 0
    N = len(Y)
    for i in range(1, N):
        x += math.log2(p(M, Y[i-1], Y[i]))
    return x/N

# get_sample('data/trwiki', 'big_sample.txt')
X, Y = split(read_file('sample0.txt'))

M = model(X, 2)
print(M[-1][-1])
PP = pp(M, Y)
print('Perplexity of {}-gram: {}'.format(2, PP))

# Ms = build_models(X)
# PPs = test_models(Ms, Y)
# for i, PP in enumerate(PPs):
#     print('Perplexity of {}-gram: {}'.format(i, PP))
