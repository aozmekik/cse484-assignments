import pandas as pd
import string
import re
import xml.etree.ElementTree as ET
from unicode_tr import unicode_tr
from unicode_tr.extras import slugify
import string


def chunks(lst, n):
    '''Yield successive n-sized chunks from lst.'''
    for i in range(0, len(lst), n):
        print('%', 100 * (i / len(lst)))
        yield lst[i:i + n]


def prepare_dataset():
    '''
        prepares the dataset for word2vec training, as stated in the homework file
    '''

    with open('dataset/wiki_00', 'r') as file:
        html = file.read()

    html = re.sub('<[^>]+>', '', html)

    c = ''
    for h in chunks(html, int(len(html) / 5)):
        h = preprocess(h)
        c += ' ' + h
    html = c

    content = ''

    df: pd.DataFrame = pd.read_csv('dataset/train.csv',
                                   usecols=['comment', 'Label'], encoding='unicode_escape')

    for index, row in df.iterrows():
        content += ' ' + row['comment']

    df = pd.read_csv('dataset/test.csv',
                     usecols=['comment', 'Label'], encoding='unicode_escape')

    for index, row in df.iterrows():
        content += ' ' + row['comment']

    # map punctuation to space
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    content = content.translate(translator)

    content = preprocess(content)

    with open('train.txt', 'w') as file:
        file.write(html + ' ' + content)


def preprocess(x):
    x = strip_numbers(x)
    x = remove_punctuation(x)
    # x = unicode_tr(x).lower()
    x = ' '.join(slugify(x).split('-'))
    x = re.sub('[^a-zA-Z]+', ' ',  x)
    x = x.strip('\n')
    x = x.replace('\n', ' ')
    x = ' '.join(x.split())  # to remove duplicate of white space
    return x.strip()


def remove_punctuation(x):
    return ''.join([w for w in x if w not in string.punctuation])


def strip_numbers(x):
    return re.sub(' +', ' ', re.sub(r'\d+', '', x)).strip()


# prepare_dataset()
