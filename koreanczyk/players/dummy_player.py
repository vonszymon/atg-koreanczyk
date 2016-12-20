import random

from koreanczyk.utils.commands import Move
from koreanczyk.utils.helpers import forward, backward


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
            for move in sorted(moves_list, reverse=True):
                if move == -1:
                    choice_group = self._random_counter_group_after_start()
                    self.my_state.state[choice_group] = backward(self.my_state.state[choice_group])
                    output.append(Move(choice_group, 'forward', move))
                else:
                    choice_group = self._random_counter_group()
                    self.my_state.state[choice_group] = forward(self.my_state.state[choice_group], move)
                    output.append(Move(choice_group, 'forward', move))
            return output

    def end(self, i):
        pass

    def _random_counter_group(self):
        not_finished_counter_groups = dict(
            (key, value) for key, value in self.my_state.state.iteritems() if value != 100)
        try:
            return random.choice(not_finished_counter_groups.keys())
        except IndexError:
            return random.choice(self.my_state.state.keys())

    def _random_counter_group_after_start(self):
        started_counter_groups = dict(
            (key, value) for key, value in self.my_state.state.iteritems() if value != -1)
        return random.choice(started_counter_groups.keys())
