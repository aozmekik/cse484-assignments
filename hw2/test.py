import random
import re
from nltk import ngrams, trigrams
from collections import Counter, defaultdict


def read_file(file):
    words = []
    with open(file, 'r', encoding='utf-8', errors='ignore') as file:
        # words = file.read().strip().split(' ')
        words = file.read()
        words = words.strip().split()
    return words


def normalize_data(data):
    # remove everything except the letters.
    return re.sub(r'[^A-Za-z. ]', '', data.lower())


def get_sample(file, sample_name, N=20):
    '''
        Gets N sample randomly from given word list and write to the file.
        @param file, name of the file containing word list.
        @param sample_name, name of the new file containing N samples.
        @param N, sample count.
    '''
    words = read_file(file)
    print(int(len(words) * (N/100)))
    words = ' '.join([words[i] for i in range(int(len(words) * (N/100)))])
    # words = ' '.join([word for word in words])
    with open(sample_name, 'w', encoding='utf-8') as file:
        file.write(words)


def model(words, n):
    if n == 1:
        # count
        counter = Counter(ngrams(words, 1))
        M = {word[0]: counter[word] for word in counter}

        # counts to probabilities
        total_count = float(sum(M.values()))
        for w in M:
            M[w] /= total_count
    else:
        # count
        M = defaultdict(lambda: defaultdict(lambda: 0))
        for w in ngrams(words, n, pad_right=True, pad_left=True):
            M[w[: n-1]][w[-1]] += 1

        # counts to probabilities
        for w1_w2 in M:
            total_count = float(sum(M[w1_w2].values()))
            for w3 in M[w1_w2]:
                M[w1_w2][w3] /= total_count

    return M


def build_models(words):
    models = []
    for n in range(1, 6):
        models.append(model(words, n))


words = read_file('sample0.txt')
models = build_models(words)
