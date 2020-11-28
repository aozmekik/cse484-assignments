import random
import re
from nltk import ngrams, trigrams
from collections import Counter, defaultdict

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
    return re.sub(r'[^A-Za-z. ]', '', X.lower().strip())


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


def smooth(M, words, n):
    Nc = defaultdict(lambda: 0)
    N = 0
    if n == 1:
        # count all the counts
        for w in M:
            c = M[w]
            Nc[c] += 1
            N += c

        # unigrams that never occured
        Nc[0] = len(words) - N

        for w in M:
            c = M[w]
            M[w] = (c + 1) * (N[c+1]/N[c])
    else:
        # count all the counts
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
                M[wi][wj] = (c + 1) * (N[c+1]/N[c])

    # revised count for ngrams that never occured
    M[None] = N[1] / N[0]


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

        # counts to probabilities
        for wi in M:
            total_count = float(sum(M[wi].values()))
            for wj in M[wi]:
                M[wi][wj] /= total_count
            M[wi][None] /= M[None]

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


def p(model, w1, w2=None):
    n = len(w1)  # size of model.
    if n == 1:  # unigram
        return model[w1]
    else:
        return model[w1][w2]


def pp(M, Y, unigram=False):
    x = 0
    N = len(Y)
    for i in range(N):
        x *= 1/p(M, Y[i], Y[i-1] if not unigram else None)
    return x**(1/N)


X, Y = split(read_file('sample0.txt'))
Ms = build_models(X)
