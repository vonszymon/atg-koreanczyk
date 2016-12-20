from koreanczyk.utils.counters import CounterGroup


class CountersState(object):
    def __init__(self):
        super(CountersState, self).__init__()
        self.state = {CounterGroup(1): -1, CounterGroup(2): -1, CounterGroup(3): -1, CounterGroup(4): -1}

    def get_counter_groups(self):
        return self.state.keys()

    def remove_group(self, group):
        return self.state.pop(group, None)

    def __str__(self):
        return self.state.__str__()

    def add_group(self, group, pos):
        self.state[group] = pos
