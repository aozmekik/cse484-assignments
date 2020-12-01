from nltk import ngrams
from collections import defaultdict
import math
import operator
import string
import random


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


def get_ngram(word, n):
    return ngrams(word, n, pad_right=True, pad_left=True, left_pad_symbol='<l>', right_pad_symbol='</l>')


def model(words, n):
    if n == 1:
        # count
        M = defaultdict(lambda: 0)
        for word in words:
            for w in get_ngram(word, n):
                M[w] += 1

    else:
        # count
        M = defaultdict(lambda: defaultdict(lambda: 0))
        for word in words:
            for w in get_ngram(word, n):
                M[w[: n-1]][w[-1]] += 1

    # smooth and counts to probabilities
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
    PPs = [pp(Ms[0], Y, 1)]
    i = 2
    for M in Ms[1:]:
        print('\tTesting {}-gram...'.format(i))
        PPs.append(pp(M, Y, i))
        i += 1
    return PPs


def p(M, w, n):
    if n == 1:  # unigram
        return M[w] if w in M else M[-1]
    else:
        w1 = w[: -1]
        if w1 in M:
            w2 = w[-1]
            if w2 in M[w1]:
                return M[w1][w2]
            else:
                return M[w1][-1]
        else:
            return M[-1][-1]


def pp(M, Y, n):
    x = 0
    N = len(Y)
    for word in Y:
        for y in get_ngram(word, n):
            x += math.log2(p(M, y, n))
    return 2**(-x/N)


def gen_S(M, n):
    # different word generating strategy has been applied to each n-gram model
    W = M
    if n != 1:
        W = {}
        for wi in M:
            for wj in M[wi]:
                if wi != -1 or wj != -1:
                    W[wi + (wj, )] = M[wi][wj]

    S = []
    total = 0
    if n == 1:
        while total < 5:
            l = max(W.items(), key=operator.itemgetter(1))[0]
            if l != -1 and '<l>' not in l and '</l>' not in l:
                S.append(l[0])
                total += 1
            del W[l]
    else:
        iter = 3 if total == 2 else 2
        while total < 2:
            l = max(W.items(), key=operator.itemgetter(1))[0]
            if l != -1 and '<l>' not in l and '</l>' not in l:
                S.append(''.join(l))
                total += 1
            del W[l]
    # randomize letters
    random.shuffle(S)
    return ''.join(S)


def test_S(Ms):
    print('Generating Sentences...')
    print('\tGenerating Sentence for: 1-gram...')
    Ss = [gen_S(Ms[0], 1)]
    for i, M in enumerate(Ms[1:]):
        print('\tGenerating Sentence for {}-gram...'.format(i+2))
        Ss.append(gen_S(M, i+2))
    return Ss


# you can get a sample from a bigger dataset.
# get_sample('data/trwiki', 'big_sample.txt', N=30)


X, Y = split(read_file('sample1.txt'))

Ms = build_models(X)
PPs = test_models(Ms, Y)

for i, PP in enumerate(PPs):
    print('Perplexity of {}-gram: {}'.format(i + 1, PP))

Ss = test_S(Ms)
for i, S in enumerate(Ss):
    print('Word for {}-gram: {}'.format(i + 1, S))
