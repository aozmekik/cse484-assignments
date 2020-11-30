import random
import re
from nltk import ngrams, trigrams
from collections import Counter, defaultdict
from sgt import SimpleGoodTuring
import numpy as np
import math
import operator
import string

# TASKS.
# TODO. produce random sentences.


def read_file(file):
    X = []
    with open(file, 'r', encoding='utf-8', errors='ignore') as file:
        X = normalize(file.read())
    return X


def normalize(X):
    print('normalizing data...')
    X = X.lower().strip()
    noise = ['style', 'text', 'align', 'left', 'width', 'table',
             'layout',  'fixed', 'border', 'valign', 'top', 'da',
             'class', 'wikitable', 'dosya', 'ico', 'jpg', 'center',
             'background', 'faff', 'padding', 'em', 'px', 'solid', 'ddd',
             'margin', 'auto', 'solid', 'ddd', 'margin', 'auto', 'cellspacing']
    for n in noise:
        X = X.replace(n, '')
    one_letter = list(string.ascii_lowercase + 'ıîâöçşiğü')
    X = X.split()
    for one in one_letter:
        X = list(filter((one).__ne__, X))
    # two_letter = [a + b for a in one_letter for b in one_letter]
    # for two in two_letter:
    #     X = X.replace(two, '')
    return X


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
    with open(sample_name, 'w', encoding='utf-8') as file:
        file.write(X)


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


def smooth_and_prob(M, words, n, wi=None):
    Nc = defaultdict(lambda: 0)
    N = 0

    if n == 1:
        # count all the counts
        N = len(M)
        for w in M:
            c = M[w]
            Nc[c] += 1

        Nc[0] = Nc[1] / N

        for w in M:
            c = M[w]
            if c not in Nc:
                gen_c(Nc, c)
            if c + 1 not in Nc:
                gen_c(Nc, c + 1)
            c = ((c + 1) * (Nc[c+1]/Nc[c]))
            M[w] = c / N
        M[-1] = Nc[0]

    else:
        for wi in M:
            for wj in M[wi]:
                c = M[wi][wj]
                Nc[c] += 1
                N += c

        # ngrams that never occured
        Nc[0] = Nc[1] / N

        # apply good turing smoothing
        for wi in M:
            total_count = float(sum(M[wi].values()))
            for wj in M[wi]:
                c = M[wi][wj]
                if c not in Nc:
                    gen_c(Nc, c)
                if c + 1 not in Nc:
                    gen_c(Nc, c + 1)
                M[wi][wj] = ((c + 1) * (Nc[c+1]/Nc[c])) / total_count
            M[wi][-1] = Nc[0] / total_count
        M[-1][-1] = Nc[0]


def model(words, n):
    if n == 1:
        # count
        counter = Counter(ngrams(words, 1))
        M = {word[0]: counter[word] for word in counter}

        # smooth and counts to probabilities
        smooth_and_prob(M, words, n)
    else:
        # count
        M = defaultdict(lambda: defaultdict(lambda: 0))
        for w in ngrams(words, n, pad_right=True, pad_left=True):
            M[w[: n-1]][w[-1]] += 1

        # smooth
        smooth_and_prob(M, words, n)
    return M


def build_models(X):
    Ms = []
    print('Building models...')
    for n in range(1, 6):
        print('\tBuilding {}-gram...'.format(n))
        Ms.append(model(X, n))
    return Ms


def test_models(Ms, Y):
    print('Testing models...')
    print('\tTesting 1-gram...')
    PPs = [pp(Ms[0], Y, unigram=True)]
    for i, M in enumerate(Ms[1:]):
        print('\tTesting {}-gram...'.format(i+1))
        PPs.append(pp(M, Y))
    return PPs


def p(M, w1, w2):
    if not w2:  # unigram
        return M[w1] if w1 in M else M[-1]
    else:
        if w1 in M:
            if w2 in M[w1]:
                return M[w1][w2]
            else:
                return M[w1][-1]
        else:
            return M[-1][-1]


def pp(M, Y, unigram=False):
    x = 0
    N = len(Y)
    for i in range(1, N):
        x += math.log2(p(M, Y[i-1], Y[i] if not unigram else None))
    return 2**(-x/N)


def gen_S(M, unigram=False):
    S = ''
    W = M
    if not unigram:
        W = {}
        for wi in M:
            for wj in M[wi]:
                if wi != -1 or wj != -1:
                    W[wi + (wj, )] = M[wi][wj]
    n = 0
    while n < 5:
        X = max(W.items(), key=operator.itemgetter(1))[0]
        if X and X != -1 and (X[0] if type(X) is tuple else True):
            if type(X) is tuple:
                if -1 in X:
                    del W[X]
                    continue
                for x in X:
                    S += ' ' + (x if x != -1 else '')
            else:
                S += ' ' + X
            n += 1
        del W[X]
            

    return S


def test_S(Ms):
    print('Generating Sentences...')
    print('\t Generating Sentence for: 1-gram...')
    Ss = [gen_S(Ms[0], unigram=True)]
    for i, M in enumerate(Ms[1:]):
        print('\tGenerating Sentence for {}-gram...'.format(i+1))
        Ss.append(gen_S(M))
    return Ss


# get_sample('data/trwiki', 'big_sample.txt', N=30)
X, Y = split(read_file('sample1.txt'))


# M = model(X, 5)
# S = gen_sentence(M)
# print(S)

Ms = build_models(X)
PPs = test_models(Ms, Y)
Ss = test_S(Ms)

for i, PP in enumerate(PPs):
    print('Perplexity of {}-gram: {}'.format(i + 1, PP))

for i, S in enumerate(Ss):
    print('Sentence for {}-gram: {}'.format(i + 1, S))
