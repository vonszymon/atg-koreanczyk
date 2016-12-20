from unittest import TestCase

from koreanczyk.game import update_board
from koreanczyk.utils.commands import Move, Merge
from koreanczyk.utils.counters import CounterGroup
from koreanczyk.utils.state import CountersState


class TestUpdate_board(TestCase):
    def test_update_board(self):
        moves = [Move(CounterGroup(1), 'forward', 3)]
        player_structs = {0: CountersState(), 1: CountersState()}

        self.assertFalse(update_board(moves, 0, player_structs))
        self.assertEqual(player_structs[0].state[CounterGroup(1)], 3)
        self.assertEqual(player_structs[0].state[CounterGroup(2)], -1)
        self.assertEqual(player_structs[0].state[CounterGroup(3)], -1)
        self.assertEqual(player_structs[0].state[CounterGroup(4)], -1)

    def test_more_moves(self):
        moves = [Move(CounterGroup(1), 'forward', 3),
                 Move(CounterGroup(2), 'forward', 4),
                 Move(CounterGroup(3), 'turn_left', 4)]
        player0_state = CountersState()
        player0_state.state[CounterGroup(3)] = 5
        player_structs = {0: player0_state, 1: CountersState()}

        self.assertFalse(update_board(moves, 0, player_structs))
        self.assertEqual(player_structs[0].state[CounterGroup(1)], 3)
        self.assertEqual(player_structs[0].state[CounterGroup(2)], 4)
        self.assertEqual(player_structs[0].state[CounterGroup(3)], 29)
        self.assertEqual(player_structs[0].state[CounterGroup(4)], -1)

    def test_knocked_opponent_counter(self):
        moves = [Move(CounterGroup(2), 'forward', 3)]
        player1_state = CountersState()
        player1_state.state[CounterGroup(1)] = 3
        player_structs = {0: CountersState(), 1: player1_state}

        self.assertTrue(update_board(moves, 0, player_structs))
        self.assertEqual(player_structs[0].state[CounterGroup(2)], 3)
        self.assertEqual(player_structs[1].state[CounterGroup(1)], -1)

    def test_knocked_opponent_group_of_counter(self):
        moves = [Move(CounterGroup(2), 'forward', 3)]
        player1_state = CountersState()
        player1_state.remove_group(CounterGroup(1))
        player1_state.remove_group(CounterGroup(2))
        player1_state.add_group(CounterGroup(1, 2), 3)
        player_structs = {0: CountersState(), 1: player1_state}

        self.assertTrue(update_board(moves, 0, player_structs))
        self.assertEqual(player_structs[0].state[CounterGroup(2)], 3)
        self.assertEqual(player_structs[1].state[CounterGroup(1)], -1)
        self.assertEqual(player_structs[1].state[CounterGroup(2)], -1)
        self.assertFalse(CounterGroup(1, 2) in player_structs[1].state)

    def test_merge_two_counters(self):
        moves = [Move(CounterGroup(2), 'forward', 3), Merge(CounterGroup(1), CounterGroup(2))]
        player0_state = CountersState()
        player0_state.state[CounterGroup(1)] = 3
        player_structs = {0: player0_state, 1: CountersState()}

        self.assertFalse(update_board(moves, 0, player_structs))
        self.assertTrue(CounterGroup(1, 2) in player_structs[0].state)
        self.assertFalse(CounterGroup(1) in player_structs[0].state)
        self.assertFalse(CounterGroup(2) in player_structs[0].state)
        self.assertEqual(player_structs[0].state[CounterGroup(1, 2)], 3)
        self.assertEqual(player_structs[0].state[CounterGroup(3)], -1)
        self.assertEqual(player_structs[0].state[CounterGroup(4)], -1)

    def test_merge_three_counters(self):
        moves = [Move(CounterGroup(3), 'forward', 3), Merge(CounterGroup(1), CounterGroup(2), CounterGroup(3))]
        player0_state = CountersState()
        player0_state.state[CounterGroup(1)] = 3
        player0_state.state[CounterGroup(2)] = 3
        player_structs = {0: player0_state, 1: CountersState()}

        self.assertFalse(update_board(moves, 0, player_structs))
        self.assertTrue(CounterGroup(1, 2, 3) in player_structs[0].state)
        self.assertFalse(CounterGroup(1) in player_structs[0].state)
        self.assertFalse(CounterGroup(2) in player_structs[0].state)
        self.assertFalse(CounterGroup(3) in player_structs[0].state)
        self.assertEqual(player_structs[0].state[CounterGroup(1, 2, 3)], 3)
        self.assertEqual(player_structs[0].state[CounterGroup(4)], -1)

    def test_two_merges(self):
        moves = [Move(CounterGroup(1), 'forward', 3),
                 Move(CounterGroup(3), 'forward', 4),
                 Merge(CounterGroup(1), CounterGroup(2)),
                 Merge(CounterGroup(3), CounterGroup(4))]
        player0_state = CountersState()
        player0_state.state[CounterGroup(2)] = 3
        player0_state.state[CounterGroup(4)] = 4
        player_structs = {0: player0_state, 1: CountersState()}

        self.assertFalse(update_board(moves, 0, player_structs))
        self.assertTrue(CounterGroup(1, 2) in player_structs[0].state)
        self.assertTrue(CounterGroup(3, 4) in player_structs[0].state)
        self.assertFalse(CounterGroup(1) in player_structs[0].state)
        self.assertFalse(CounterGroup(2) in player_structs[0].state)
        self.assertFalse(CounterGroup(3) in player_structs[0].state)
        self.assertFalse(CounterGroup(4) in player_structs[0].state)
        self.assertEqual(player_structs[0].state[CounterGroup(1, 2)], 3)
        self.assertEqual(player_structs[0].state[CounterGroup(3, 4)], 4)

    def test_lose_round_when_do_move_and_all_are_minus_1(self):
        # todo - not here
        pass


def _print(dictionary):
    for k, v in dictionary.iteritems():
        print k, v
