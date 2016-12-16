class CountersState(object):
    def __init__(self):
        super(CountersState, self).__init__()
        self.state = {'1': -1, '2': -1, '3': -1, '4': -1}

    def get_counter_groups(self):
        return self.state.keys()

    def remove_group(self, group):
        return self.state.pop(group, None)

    def add_group(self, group, pos):
        self.state[group] = pos
