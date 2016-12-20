class CounterGroup(object):
    def __init__(self, *args):
        super(CounterGroup, self).__init__()
        self.counter_set = frozenset(x for x in args)

    def __hash__(self):
        return hash(self.counter_set)

    def _describe_counter_set(self):
        return ','.join(str(x) for x in self.counter_set)

    def __eq__(self, other):
        if isinstance(other, CounterGroup):
            return self.counter_set == other.counter_set
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "CounterGroup(%s)" % self._describe_counter_set()
