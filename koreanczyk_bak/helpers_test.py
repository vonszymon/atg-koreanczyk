from helpers import *


def test_forward_rectangle_path():
    for i in range(20):
        assert forward(i, 1) == i + 1 if i + 1 < 20 else 100
        assert forward(i, 2) == i + 2 if i + 2 < 20 else 100
        assert forward(i, 3) == i + 3 if i + 3 < 20 else 100
        assert forward(i, 4) == i + 4 if i + 4 < 20 else 100
        assert forward(i, 5) == i + 5 if i + 5 < 20 else 100


def test_turning_left():
    assert turn_left(5, 1) == 21
    assert turn_left(5, 2) == 22
    assert turn_left(5, 3) == 23
    assert turn_left(5, 4) == 24
    assert turn_left(5, 5) == 25

    assert turn_left(10, 1) == 26
    assert turn_left(10, 2) == 27
    assert turn_left(10, 3) == 28
    assert turn_left(10, 4) == 29
    assert turn_left(10, 5) == 30

    assert turn_left(23, 1) == 41
    assert turn_left(23, 2) == 42
    assert turn_left(23, 3) == 100
    assert turn_left(23, 4) == 100
    assert turn_left(23, 5) == 100


def test_forward_left_down_diagonal():
    result_positions = [22, 23, 24, 25, 15, 16, 17, 18, 19]
    for current in [21, 22, 23, 24, 25]:
        for x in range(1, 6):
            assert forward(current, x) == result_positions[result_positions.index(current)+x]


def test_forward_left_up_diagonal():
    result_positions = [27, 28, 29, 30, 100, 100, 100, 100, 100]
    for current in [26, 27, 28, 29, 30]:
        for x in range(1, 6):
            assert forward(current, x) == result_positions[result_positions.index(current)+x]


def test_backward():
    special = [0, 1, 21, 26, 41]
    special_results = [0, 100, 5, 10, 23]
    for i, s in enumerate(special):
        assert backward(s) == special_results[i]

    for x in range()


if __name__ == '__main__':
    test_forward_rectangle_path()
    test_turning_left()
    test_forward_left_down_diagonal()
    test_forward_left_up_diagonal()
    test_backward()


