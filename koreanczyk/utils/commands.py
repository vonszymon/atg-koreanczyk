class Merge(object):
    def __init__(self, group1, group2):
        self.group1 = group1
        self.group2 = group2


class Move(object):
    def __init__(self, counter_group_id, command, of):
        super(Move, self).__init__()
        self.counter_group_id = counter_group_id
        self.command = command
        self.of = of

    @property
    def counter_group_id(self):
        return self.counter_group_id

    @property
    def command(self):
        return self.command

    @property
    def of(self):
        return self.of
