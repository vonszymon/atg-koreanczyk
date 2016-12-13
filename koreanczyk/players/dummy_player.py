class Player(object):
    def __init__(self):
        super(Player, self).__init__()
        self.i = -1

    def name(self, i):
        self.i = i

    def paticks(self, i):
        return ['X', 'X']
