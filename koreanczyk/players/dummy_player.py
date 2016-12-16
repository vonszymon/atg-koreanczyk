class Player(object):
    def __init__(self):
        super(Player, self).__init__()
        self.i = -1

    def name(self, i):
        self.i = i

    def board(self, i, player_structs):
        # todo
        # """'board' input format: {
        #     0: [['1', 4], ['23', 15], ['4': 6]],
        #     1: [['1', 4], ['2', 15], ['3': 6], ['4', 100]}"""
        # self.board = board[self.i]  # save only my board

        pass

    def paticks(self, i):
        """Output format, e.g.: ['X', 'O']"""
        return ['X', 'X']

    def throw_result(self, i, s):
        if s in ['yut', 'mo']:
            # throwing again
            pass

    def moves(self, i, moves_list):
        """Input format: [1, 3, -1],
        Output format, e.g.: [Move('1','forward', 3), Move('23', 'turn_left', 5), Merge('1', '2')] """
        if i == self.i:
            output = []
            for (idx, move) in enumerate(moves_list, 1):
                output.append({str(idx): ['forward', move]})
            return output

    def end(self, i):
        pass
