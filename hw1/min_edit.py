def sub_cost(x, y):
    if x == y:
        return 0
    else:
        return 2


def min_edit_distance(source, target):
    n, m = len(source), len(target)

    D = [[0 for j in range(m+1)] for i in range(n+1)]
    D[0][0] = 0

    for i in range(1, n+1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, m+1):
        D[0][j] = D[0][j-1] + 1

    for i in range(1, n+1):
        for j in range(1, m+1):
            D[i][j] = min(D[i-1][j] + 1, D[i-1][j-1] + sub_cost(source[i-1], target[j-1]), D[i][j-1] + 1)


    return D[n][m]


print(min_edit_distance('selamlar', 'ayaklanalım'))