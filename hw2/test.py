from nltk import ngrams
import random


def read_file(file):
    words = []
    with open(file, 'r', encoding='utf-8', errors='ignore') as file:
        # words = file.read().strip().split(' ')
        words = file.read()
        words = words.strip().split()
    return words


def get_sample(file, sample_name, N=20):
    '''
        Gets N sample randomly from given word list and write to the file.
        @param file, name of the file containing word list.
        @param sample_name, name of the new file containing N samples.
        @param N, sample count.
    '''
    words = read_file(file)
    words = ' '.join([words[i] for i in range(int(len(words) * (N/100)))])
    # words = ' '.join([word for word in words])
    with open(sample_name, 'w', encoding='utf-8') as file:
        file.write(words)

def 


get_sample('data/trwiki', 'sample0.txt')



# words = read_file('data/trwiki')

# n = 6
# sixgrams = ngrams(words, n)

# for grams in sixgrams:
#   print(grams)