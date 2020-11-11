import random

MAX_CHAR_LONG = 15
DICT = ['selamlar', 'olsun', 'sana', 'ey', 'yüce', 'dostlar']


def read_file(file):
    lines = []
    with open(file) as file:
        lines = file.read().splitlines()
    return lines


def get_sample(word_list, sample_name, N=1000):
    '''
        Gets N sample randomly from given word list and write to the file.
        @param word_list, name of the file containing word list.
        @param sample_name, name of the new file containing N samples.
        @param N, sample count.
    '''
    lines = read_file(word_list)
    words = '\n'.join([random.choice(lines) for i in range(N)])
    with open(sample_name, 'w') as file:
        file.write(words)


def create_dataset():
    for i in range(5):
        # FIXME fix the names.
        get_sample('dataset/data.txt', 'dataset/sample{}.txt'.format(i))


def sub_cost(x, y):
    if x == y:
        return 0
    else:
        return 2


def find_cost(source, target, d, i, j):
    d[i][j] = min(d[i-1][j] + 1, d[i-1][j-1] +
                  sub_cost(source[i-1], target[j-1]), d[i][j-1] + 1)


def fill_diagon(source, target, d, i, j):
    # fill in the cells required to fill the diagon.
    for ix in range(1, i):  # above col.
        find_cost(source, target, d, ix, j)
    for jy in range(1, j):  # left row.
        find_cost(source, target, d, i, jy)

    find_cost(source, target, d, i, j)

    # find and save the next diagon position.
    diagon_i = i if i + 1 == len(d) else i + 1
    diagon_j = j if j + 1 == len(d[0]) else j + 1
    set_cursor(d, diagon_i, diagon_j)

    return d[i][j]


def get_cursor(d):
    return (1, 1) if isinstance(d[0][0], int) else d[0][0]


def set_cursor(d, i, j):
    d[0][0] = (i, j)


def is_untouched(d, i, j):
    return d[i][j] == 0 and not (i == 0 and j == 0)


def table_length(word):
    return min(MAX_CHAR_LONG, len(word)) + 1


def is_finished(d, i, j):
    return len(d[0]) == j + 1 and len(d) == i + 1 and not is_untouched(d, i, j)


def fill(source, target, d, cost):
    matrix_cost = cost

    i, j = get_cursor(d)
    finished = is_finished(d, i, j)
    while matrix_cost <= cost and not finished:
        i, j = get_cursor(d)

        # prevent finding diagon again.
        matrix_cost = fill_diagon(
            source, target, d, i, j) if is_untouched(d, i, j) else d[i][j]
        
        finished = is_finished(d, i, j)
    return finished


def enhanced_min_edit(source, word_dict):
    # length of source string.
    n = table_length(source)

    D = [[[0 for _ in range(table_length(word))]
          for _ in range(n)] for word in word_dict]

    # fill first row and column of each word in vector.
    for d in D:
        for i in range(1, n):
            d[i][0] = d[i - 1][0] + 1
        for j in range(1, len(d[0])):
            d[0][j] = d[0][j-1] + 1


    found = []
    for cost in range(MAX_CHAR_LONG):  # filling jth cost.
        for i, d in enumerate(D):  # traverse D vector.
            if fill(source, word_dict[i], d, cost):
                found.append(i)


def menu():
    word_dict = read_file('sample0.txt')
    source = input('Enter the main word: ')

    words = enhanced_min_edit(source, word_dict)


enhanced_min_edit('selamlar', read_file('dataset/sample.txt'))
