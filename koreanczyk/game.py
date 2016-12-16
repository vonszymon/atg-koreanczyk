from random import seed, randint
from sys import argv

from koreanczyk.utils.commands import Merge, Move
from koreanczyk.utils.state import CountersState
from koreanczyk.utils.helpers import forward, turn_left, same_place

GAMES_TO_PLAY = 11
output = {"do": -1, "gae": 2, "geol": 3, "yut": 4, "mo": 5}
again = {"yut": True, "mo": True, "do": False, "gae": False, "geol": False}
number_of_x_to_output = {0: "yut", 1: "geol", 2: "gae", 3: "do", 4: "mo"}


def get_output(inputs):
    """Return name of throw result, e.g.:
        XXXO -> 'do',
        OOOX -> 'geol'"""
    inputs = map(lambda x: x.upper(), inputs)
    number_of_x = len(filter(lambda e: e == "X", inputs))
    return number_of_x_to_output[number_of_x]


def message(kind, msg):
    print "### KOREANCZYK( %s ): %s" % (kind, msg)


def create_players(player1, player2):
    """Import players, call `name` method and return array of players."""
    players = [__import__(player1).Player(),
               __import__(player2).Player()]

    for p in range(len(players)):
        players[p].name(p)

    return players


def games(player1, player2):
    """Run specified amount of rounds and return scores."""
    scores = [0, 0]

    message("START SERIES", str([player1, player2]))
    players = create_players(player1, player2)
    for i in range(GAMES_TO_PLAY):
        message("GAME START", str(i + 1))
        scores += game(players)

    message("SERIES RESULT", "{}({})  {}({})".format(player1, scores[0], player2, scores[1]))

    return scores


def _check_no_counters_on_board_and_do_move(results, actual_player, player_structs):
    # there is no possibility to get more than one 'do' move
    only_do_move = len(results) == 1 and results[0] == -1
    no_counters_on_board = set(player_structs[actual_player].state.values()) == {-1}
    return only_do_move and no_counters_on_board


def game(players):
    player_structs = {0: CountersState(), 1: CountersState()}
    actual_player = randint(0, 1)

    while True:
        players[0].board(actual_player, player_structs)
        players[1].board(actual_player, player_structs)

        results = throws(actual_player, players)
        if _check_no_counters_on_board_and_do_move(results, actual_player, player_structs):
            actual_player = other_player(actual_player)
            continue

        if actual_player == 0:
            moves_from_player = players[0].moves(actual_player, results)
            players[1].moves(actual_player, results)
        else:
            players[0].moves(actual_player, results)
            moves_from_player = players[1].moves(actual_player, results)

        are_valid_moves = validate_moves(moves_from_player, results, actual_player, player_structs)
        if not are_valid_moves:
            winner(other_player(actual_player), players)
        extra_throws = update_board(moves_from_player, actual_player, player_structs)
        if check_win(actual_player, player_structs):
            winner(actual_player, players)
        if not extra_throws:
            actual_player = other_player(actual_player)


def winner(winner_player, players):
    result = [0, 0]
    result[winner_player] = 1
    players[0].end(winner_player)
    players[1].end(winner_player)
    return result


def throws(i, players):
    """Return e.g.: [1, 3, -1]"""
    throw = players[0].paticks(i) + players[1].paticks(i)
    result = get_output(throw)
    results = [result]
    players[0].throw_result(i, result)
    players[1].throw_result(i, result)
    throwing_again = again[result]
    while throwing_again:
        throw = players[0].paticks(i) + players[1].paticks(i)
        result = get_output(throw)
        results.append(result)

        players[0].throw_result(i, result)
        players[1].throw_result(i, result)

        throwing_again = again[result]

    return map(lambda x: output[x], results)


def other_player(actual_player):
    return 1 - actual_player


def check_win(actual_player, player_structs):
    return set(player_structs[actual_player].state.values()) == {100}


def _apply_moves(moves, actual_player, player_structs):
    result = {}
    for move in moves:
        if move.command == "forward":
            result[move.counter_group_id] = forward(player_structs[actual_player].state[move.counter_group_id], move.of)
        else:  # "turn_left"
            result[move.counter_group_id] = turn_left(player_structs[actual_player].state[move.counter_group_id],
                                                      move.of)
    return result


def validate_moves(moves_from_player, results, actual_player, player_structs):
    moves = filter(lambda x: isinstance(x, Move), moves_from_player)  # get only Move commands
    # validating groups
    groups = map(lambda x: x.counter_group_id, moves)
    valid_groups = player_structs[0].get_counter_groups()
    validated_groups = all(g in valid_groups for g in groups)

    # validating moves
    player_moves = map(lambda x: x.of(), moves)
    validated_moves = sorted(results) == sorted(player_moves)

    if validated_groups and validated_moves:
        # validating 'merge' commands
        counters_new_position = _apply_moves(moves, actual_player, player_structs)
        merges = filter(lambda x: isinstance(x, Merge), moves_from_player)
        for merge in merges:
            if not same_place(counters_new_position[merge.group1], counters_new_position[merge.group2]):
                return False

    return True


def _knock_counter_group(other_counter_group, player, player_structs):
    #todo:
    # * set to -1
    # * split groups
    pass


def update_board(moves, actual_player, player_structs):
    only_moves = filter(lambda x: isinstance(x, Move), moves)
    for move in only_moves:
        if move.command == "forward":
            player_structs[actual_player].state = forward(player_structs[actual_player].state, move.of)
        else:  # turn_left
            player_structs[actual_player].state = turn_left(player_structs[actual_player].state, move.of)
    only_merges = filter(lambda x: isinstance(x, Merge), moves)
    for merge in only_merges:
        place1 = player_structs[actual_player].remove_group(merge.group1)
        place2 = player_structs[actual_player].remove_group(merge.group2)
        new_group_name = "".join(sorted([merge.group1, merge.group2]))
        player_structs[actual_player].add_group(new_group_name, max(place1, place2))

    extra_round_for_knocked = False
    for counter_group, place in player_structs[actual_player].state.iteritems():
        for other_counter_group, other_place in player_structs[other_player(actual_player)].iteritems():
            if same_place(place, other_place):
                _knock_counter_group(other_counter_group, other_player(actual_player), player_structs)
                extra_round_for_knocked = True

    return extra_round_for_knocked


if __name__ == "__main__":
    seed()
    if len(argv) < 3:
        print "Invocation:"
        print "   game player1 player2"
        exit()

    print games(argv[1], argv[2])
