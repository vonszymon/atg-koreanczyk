from unittest import TestCase

from koreanczyk.game import throws


class TestThrows(TestCase):
    def test_throws_without_extra_round(self):
        players1 = {0: MockPlayer([['X', 'X']]),
                    1: MockPlayer([['X', 'O']])}
        players2 = {0: MockPlayer([['X', 'X']]),
                    1: MockPlayer([['O', 'O']])}
        players3 = {0: MockPlayer([['X', 'O']]),
                    1: MockPlayer([['O', 'O']])}
        self.assertEqual([-1], throws(0, players1))
        self.assertEqual([2], throws(0, players2))
        self.assertEqual([3], throws(0, players3))

    def test_throws_with_extra_rounds(self):
        players = {0: MockPlayer([['X', 'X'], ['O', 'O'], ['O', 'O']]),
                   1: MockPlayer([['X', 'X'], ['O', 'O'], ['X', 'X']])}
        self.assertEqual([5, 4, 2], throws(0, players))


class MockPlayer(object):
    def __init__(self, sequence):
        super(MockPlayer, self).__init__()
        self.sequence = sequence

    def paticks(self, _):
        return self.sequence.pop(0)

    def throw_result(self, i, result):
        pass
