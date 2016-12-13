#  O o o o o O
#  o o     o o
#  o   o o   o
#  o    O    o
#  o   o o   o
#  o o     o o
#  O o o o o O

MOVES = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
         [0, 1, 2, 3, 4, 5, 21, 22, 23, 24, 25, 15, 16, 17, 18, 19],
         [0, 1, 2, 3, 4, 5, 21, 22, 23, 41, 42],
         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 26, 27, 28, 29, 30]]


# helper:
# * forward()
# * turn_left()


#  10   9   8        7   6     5
#  11  26               21     4
#  12      27       22         3
#             23/28
#  13      24       29/41      2
#  14  25               30/42  1
#  15  16  17       18  19     0


def turn_left(current, i):
    if current not in [5, 10, 23]:
        raise ValueError("Current position not on the crossroad (i.e.: [5, 10, 23])")
    idx_list = -1
    for x in range(len(MOVES)):
        try:
            MOVES[x].index(current)
            idx_list = x
            break
        except ValueError:
            pass
    idx_list += 1
    while True:
        try:
            idx = MOVES[idx_list].index(current)
            break
        except ValueError:
            idx_list += 1
    try:
        result_idx = MOVES[idx_list][idx + i]
    except IndexError:
        return 100
    return result_idx


def backward(current):
    if current == 0:
        return 0
    if current == 1:
        return 100
    if current == 21:
        return 5
    if current == 26:
        return 10
    if current == 41:
        return 23
    return current-1


def forward(current, i):
    _list = []
    idx = -1
    for moves_list in MOVES:
        try:
            idx = moves_list.index(current)
            _list = moves_list
            break
        except ValueError:
            pass
    try:
        result_idx = _list[idx + i]
    except IndexError:
        return 100
    return result_idx






assert forward(21, 1) == 22
assert forward(21, 2) == 23
assert forward(21, 3) == 24
assert forward(21, 4) == 25
assert forward(21, 5) == 15

assert forward(22, 1) == 23
assert forward(22, 2) == 24
assert forward(22, 3) == 25
assert forward(22, 4) == 15
assert forward(22, 5) == 16

assert forward(23, 1) == 24
assert forward(23, 2) == 25
assert forward(23, 3) == 15
assert forward(23, 4) == 16
assert forward(23, 5) == 17

assert forward(24, 1) == 25
assert forward(24, 2) == 15
assert forward(24, 3) == 16
assert forward(24, 4) == 17
assert forward(24, 5) == 18

assert forward(25, 1) == 15





assert forward(26, 1) == 27
assert forward(26, 2) == 28
assert forward(26, 3) == 29
assert forward(26, 4) == 30
assert forward(26, 5) == 100

assert forward(27, 1) == 28
assert forward(28, 1) == 29
assert forward(29, 1) == 30



assert forward(15, 1) == 16

assert forward(21, 1) == 22
assert forward(21, 2) == 23
assert forward(21, 3) == 24
assert forward(21, 4) == 25
assert forward(21, 5) == 15

assert forward(22, 1) == 23
assert forward(22, 2) == 24
assert forward(22, 3) == 25
assert forward(22, 4) == 15
assert forward(22, 5) == 16


# assert forward(30, 1) == x

#  10   9   8        7   6   5
#  11  26               21   4
#  12      27       22       3
#             23/28
#  13      24       29       2
#  14  25               30   1
#  15  16  17       18  19   0




# assert turn_left(5, )
