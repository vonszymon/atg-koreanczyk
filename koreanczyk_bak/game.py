from random import seed
from sys import argv

GAMES_TO_PLAY = 50
output = {"do": -1, "gae": 2, "geol": 3, "yut": 4, "mo": 5}
again = {"yut": True, "mo": True, "do": False, "gae": False, "geol": False}
number_of_x_to_output = {0: "yut", 1: "geol", 2: "gae", 3: "do", 4: "mo"}



# information on board
# (player, counter_id, position (x, y))
# (1, 1, (x, y))

# move:
# (counter_id,

def get_output(inputs):
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


def game(players):
    board = [[0 for _ in range(5)] for _ in range(5)]
    actual_player = 0 #todo maybe random player at the beginning?
    players[0].board(actual_player, board)
    players[1].board(actual_player, board)

    while True:
        # THROWS
        throw = players[0].paticks(actual_player) + players[1].paticks(actual_player)
        result = get_output(throw)
        results = [result]

        players[0].throw_result(actual_player, result)
        players[1].throw_result(actual_player, result)

        throwing_again = again[result]

        while throwing_again:
            throw = players[0].paticks(actual_player) + players[1].paticks(actual_player)
            result = get_output(throw)
            results += result

            players[0].throw_result(actual_player, result)
            players[1].throw_result(actual_player, result)

            throwing_again = again[result]

        if actual_player == 0:
            moves_from_player = players[0].moves(actual_player, results)
            players[1].moves(actual_player, results)
        else:
            players[0].moves(actual_player, results)
            moves_from_player = players[1].moves(actual_player, results)

        validate_moves(moves_from_player, results)
        board = update_board(moves_from_player, actual_player, board)

        # if somebody_won()

        players[0].end(actual_player)
        players[1].end(actual_player)

        actual_player = 1 - actual_player

    return [0, 1]

def somebody_won():
    return False

def validate_moves(moves_from_player, results):
    return all(validate_move(move, results) for move in moves_from_player)


def validate_move(move, results):
    # todo implement
    return True


def update_board(moves, actual_player, board):
    # todo implement update
    return board


if __name__ == "__main__":
    seed()
    if len(argv) < 3:
        print "Invocation:"
        print "   game player1 player2"
        exit()

    print games(argv[1], argv[2])
