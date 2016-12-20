import random

from koreanczyk.utils.commands import Move


class Player(object):
    def __init__(self):
        super(Player, self).__init__()
        self.i = -1

    def name(self, i):
        self.i = i

    def board(self, i, player_structs):
        self.my_state = player_structs[self.i]

    def paticks(self, i):
        """Output format, e.g.: ['X', 'O']"""
        amount_x = random.randint(0, 2)
        return amount_x * ['X'] + (2 - amount_x) * ['O']

    def throw_result(self, i, s):
        if s in ['yut', 'mo']:
            # throwing again
            pass

    def moves(self, i, moves_list):
        """Input format: [1, 3, -1],
        Output format, e.g.: [Move(CounterGroup(1),'forward', 3), Move(CounterGroup(2, 3), 'turn_left', 5), Merge(CounterGroup(1), CounterGroup(2))] """
        if i == self.i:
            output = []
            for move in moves_list:
                output.append(Move(self._random_counter_group(), 'forward', move))
            return output

    def end(self, i):
        pass

    def _random_counter_group(self):
        not_finished_counter_groups = dict((key, value) for key, value in self.my_state.iteritems() if value != 100)
        return random.choice(not_finished_counter_groups.keys())
