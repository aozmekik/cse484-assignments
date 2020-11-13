import random

MAX_CHAR_LONG = 15


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
        get_sample('dataset/data.txt', 'dataset/sample{}.txt'.format(i))


def sub_cost(x, y):
    if x == y:
        return 0
    else:
        return 2


def find_cost(source, target, d, i, j):
    d[i][j] = min(d[i-1][j] + 1, d[i-1][j-1] +
                  sub_cost(source[i-1], target[j-1]), d[i][j-1] + 1)
    return d[i][j]


def get_cursor(d):
    return (1, 0) if isinstance(d[0][0], int) else d[0][0]


def set_cursor(d, i, cost):
    d[0][0] = (i, cost)


def is_untouched(d, i, j):
    return d[i][j] == -1


def table_length(word):
    return min(MAX_CHAR_LONG, len(word)) + 1


def is_finished(d, i):
    return len(d) == i + 1 and not is_untouched(d, i, len(d[0]) - 1)


def is_found(d, i, cost):
    return is_finished(d, i) and d[i][-1] <= cost


def fill_row(source, target, d, i):
    min_cost = MAX_CHAR_LONG
    margin = len(d[0]) - len(d) if len(d[0]) > len(d) else 1

    for jy in range(1, len(d[0])):
        cost = find_cost(source, target, d, i, jy)
        if jy >= margin + i:
            min_cost = min(cost, min_cost)

    set_cursor(d, i+1, min_cost)
    return min_cost


def fill(source, target, d, cost):
    i, row_cost = get_cursor(d)

    go = row_cost <= cost
    found = is_found(d, i - 1, cost)
    while go and not found:
        i, row_cost = get_cursor(d)

        row_cost = fill_row(source, target, d, i)

        found = is_found(d, i, cost)
        go = row_cost <= cost
    return found


def report_density(D):
    total_cell, touched_cell = 0, 0
    for d in D:
        n, m = len(d), len(d[0])
        total_cell += n * m
        touched_cell += n + m - 1
        for i in range(1, n):
            for j in range(1, m):
                if not is_untouched(d, i, j):
                    touched_cell += 1
    print('Occupied percentage of dynamic programming table: {:.3}'.format(
        touched_cell / total_cell))


def report_found(D, word_dict, found):
    print('Top {} words with their edit distance'.format(len(found)))
    for i in found:
        d = D[i]
        word = word_dict[i]
        edit_distance = d[-1][-1]
        print('Word: {}, Edit Distance: {}'.format(word, edit_distance))


def enhanced_min_edit(source, word_dict):
    # length of source string.
    n = table_length(source)

    D = [[[-1 for _ in range(table_length(word))]
          for _ in range(n)] for word in word_dict]

    # fill first row and column of each word in vector.
    for d in D:
        d[0][0] = 0
        for i in range(1, n):
            d[i][0] = d[i - 1][0] + 1
        for j in range(1, len(d[0])):
            d[0][j] = d[0][j-1] + 1

    found = set()
    for cost in range(MAX_CHAR_LONG):  # filling jth cost.
        if len(found) != 5:  # top 5 words.
            for i, d in enumerate(D):  # traverse D vector.
                if fill(source, word_dict[i], d, cost):
                    found.add(i)
                    if len(found) == 5:
                        break

    report_density(D)
    report_found(D, word_dict, found)


def menu():
    word_dict = read_file('dataset/sample1.txt')
    source = input('Enter the main word: ')

    words = enhanced_min_edit(source, word_dict)


menu()
# enhanced_min_edit('selam', ['helyum'])
