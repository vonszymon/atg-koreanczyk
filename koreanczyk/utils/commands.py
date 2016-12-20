class Merge(object):
    def __init__(self, *groups):
        self.groups = groups

    def __str__(self):
        return str(self.groups)


class Move(object):
    def __init__(self, counter_group_id, command, of):
        super(Move, self).__init__()
        self.counter_group_id = counter_group_id
        self.command = command
        self.of = of

    def counter_group_id(self):
        return self.counter_group_id

    def command(self):
        return self.command

    def of(self):
        return self.of

    def __str__(self):
        return "Move(%s, %s, %d)" % (str(self.counter_group_id), self.command, self.of)
