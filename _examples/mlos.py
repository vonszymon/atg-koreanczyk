from random import *
from collections import defaultdict
import traceback
from copy import copy
from math import log

ROUNDS = 30
CLIP_MAX = 3

DODGE = 'UNIK'
LOAD = 'LADUJ'
DEAD = 'DEAD'
SHOOT_AT = 'STRZEL {}'


def shoot(guy):
    return SHOOT_AT.format(guy.name)


############################################################
# Utilities
############################################################

def get_target(action):
    return int(action[-1])


def flip_coin(self, p):
    return random() < p


def choose(options):
    x = random()
    s = 0
    for v, p in options.iteritems():
        s += p
        if x < s:
            return v
    return iter(options).next()


def always(option):
    return {option: 1.0}


def product(o1, o2):
    return {
        (a, b): p * s
        for a, p in o1.iteritems()
        for b, s in o2.iteritems()
        }


def scale(options, s):
    return {o: p * s for o, p in options.iteritems()}


def combine(*branches):
    res = defaultdict(float)
    total = sum(p for _, p in branches)

    for options, p in branches:
        for v, s in options.iteritems():
            res[v] += s * p / total

    return res


def without(options, o):
    try:
        p = options[o]
        if p != 1.0:
            res = scale(options, 1 / (1 - p))
            del res[o]
            return res
        else:
            return {}
    except KeyError:
        return options


def print_options(options):
    for k, p in options.iteritems():
        # print '  {:30} :  {:>7.2%}'.format(k, p)
        pass


def print_guy(guy):
    # print 'Guy {}'.format(guy.name)
    # print '  {}'.format('alive' if guy.alive else 'dead')
    # print '  clip:   {} / {}'.format(guy.clip, CLIP_MAX)
    # print '  dodged: {}'.format(guy.dodged)
    pass


def report_exc(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            raise

    return wrapper


def build_histogram(data, target):
    hist = defaultdict(int)

    for item, count in data.iteritems():
        val = target(item)
        hist[val] += count

    return hist


def dist_from_histogram(histogram):
    total = float(sum(histogram.values()))
    return {
        x: count / total
        for x, count in histogram.iteritems()
        }


def plogp(p):
    return 0 if p == 0 else p * log(p, 2)


def entropy(dist):
    return - sum(plogp(p) for p in dist.itervalues())


############################################################
# Decision tree
############################################################

def with_name(name):
    def wrapper(f):
        f.__name__ = name
        return f

    return wrapper


def entropy_from_data(data, target):
    hist = build_histogram(data, target)
    dist = dist_from_histogram(hist)
    return entropy(dist)


def indent(text, count):
    padding = ' ' * count
    return '\n'.join((padding + line) for line in text.split('\n'))


def dist2str_oneline(dist):
    return ',   '.join('{}: {:.2%}'.format(k, p) for k, p in dist.iteritems())


class Node(object):
    def __init__(self, attr, dist, size, children):
        self.attr = attr
        self.dist = dist
        self.size = size
        self.children = children

    def __format_child(self, child):
        if isinstance(child, Node):
            return str(child)
        else:
            dist, size = child
            return '{}: '.format(size) + dist2str_oneline(dist)

    def __str__(self):
        name = self.attr.__name__
        dist = dist2str_oneline(self.dist)

        s = '{}: [{}] {}\n'.format(name, self.size, dist)

        sub = '\n'.join(
            '{}: {}'.format(v, self.__format_child(sub))
            for v, sub in self.children.iteritems()
        )
        return s + indent(sub, count=2)

    def __repr__(self):
        return str(self)


def partition_by_attr(data, attr):
    parts = defaultdict(lambda: defaultdict(int))

    for item, count in data.iteritems():
        v = attr(item)
        parts[v][item] += count

    return parts


def choose_best_attribute(data, target, attrs, H):
    # H = entropy_from_data(data, target)
    # print 'Entropy: {}'.format(H)

    best = None
    best_parts = None
    max_gain = -1

    for a in attrs:
        hist = build_histogram(data, a)
        dist = dist_from_histogram(hist)
        parts = partition_by_attr(data, a)

        Ha = [
            entropy_from_data(part, target) * dist[v]
            for v, part in parts.iteritems()
            ]
        gain = H - sum(Ha)
        # print 'gain for {}: {}'.format(a.__name__, gain)
        if gain > max_gain:
            max_gain = gain
            best = a
            best_parts = parts

    return (best, best_parts, gain)


def build_tree(data, target, attrs, total_size=None):
    size = sum(data.values())

    if total_size is None:
        total_size = size

    data_hist = build_histogram(data, target)
    data_dist = dist_from_histogram(data_hist)
    H = entropy(data_dist)

    min_size = 0.03
    if not attrs or H == 0 or float(size) / total_size < min_size:
        return (data_dist, size)

    a, parts, gain = choose_best_attribute(data, target, attrs, H)

    if gain == 0:
        return (data_dist, size)

    attrs = copy(attrs)
    attrs.remove(a)

    subtrees = {}

    for val, sample in parts.iteritems():
        subtrees[val] = build_tree(sample, target, attrs, total_size)

    return Node(a, data_dist, size, subtrees)


def search_tree(root, data):
    if isinstance(root, Node):
        val = root.attr(data)
        if val in root.children:
            return search_tree(root.children[val], data)
        else:
            return (root.dist, root.size)
    else:
        return root


g0_alive = with_name('g0_alive')(lambda s: s[0][0])
g0_dodged = with_name('g0_dodged')(lambda s: s[0][1])
g0_clip = with_name('g0_clip')(lambda s: s[0][2])

g1_alive = with_name('g1_alive')(lambda s: s[1][0])
g1_dodged = with_name('g1_dodged')(lambda s: s[1][1])
g1_clip = with_name('g1_clip')(lambda s: s[1][2])

g2_alive = with_name('g2_alive')(lambda s: s[2][0])
g2_dodged = with_name('g2_dodged')(lambda s: s[2][1])
g2_clip = with_name('g2_clip')(lambda s: s[2][2])

g_action = with_name('action')(lambda s: s[3])

state_params = [
    g0_alive, g0_dodged, g0_clip,
    g1_alive, g1_dodged, g1_clip,
    g2_alive, g2_dodged, g2_clip,
]


############################################################
# Classes
############################################################

class Cowboy(object):
    """ Simple data holder for each cowboy's state """

    def __init__(self, **kwargs):
        self.reset()
        if 'name' in kwargs:
            self.name = kwargs['name']

    def reset(self):
        self.clip = 0
        self.alive = True
        self.dodged = False

    @property
    def dead(self):
        return not self.alive

    @property
    def can_dodge(self):
        return self.alive and not self.dodged

    @property
    def can_shoot(self):
        return self.alive and not self.empty

    @property
    def can_load(self):
        return self.alive and not self.full

    @property
    def empty(self):
        return self.clip == 0

    @property
    def full(self):
        return self.clip == CLIP_MAX

    @property
    def state(self):
        return (self.alive, self.dodged, self.clip)

    def act_load(self):
        self.dodged = False
        self.clip += 1

    def act_shoot(self):
        self.dodged = False
        self.clip -= 1

    def act_dodge(self):
        self.dodged = True

    def __copy__(self):
        o = Cowboy()
        o.name = self.name
        o.clip = self.clip
        o.alive = self.alive
        o.dodged = self.dodged
        o.stats = self.stats
        return o

    def __str__(self):
        return 'Guy[{}]'.format(self.name)

    def __repr__(self):
        return str(self)


class CowboyStats(object):
    def __init__(self, name):
        self.name = name
        self.won = 0
        n = 2
        self.first_moves = [defaultdict(int) for _ in xrange(n)]
        self.reactions = defaultdict(lambda: defaultdict(int))
        self.kills = defaultdict(int)
        self.score = 0.0

        self.correct = 0
        self.moves = 0

    @property
    def total_kills(self):
        return sum(self.kills.values())

    def next_game(self):
        pass

    def save_action(self, state, action):
        self.reactions[state][action] += 1

    def action_dist(self, state, round):
        moves = self.first_moves[round - 1]
        total = sum(moves.values())
        return {
            action: n / float(total)
            for action, n in moves.iteritems()
            }

    def build_decision_tree(self):
        data = {
            (g1, g2, g3, action): n
            for (g1, g2, g3), stats in self.reactions.iteritems()
            for action, n in stats.iteritems()
            }
        self.tree = build_tree(data, g_action, state_params)


class Predictor(object):
    def __init__(self):
        self.stats = {
            n: CowboyStats(n)
            for n in xrange(3)
            }
        self.round = 0
        self.game = 0

    def next_game(self, guys):
        self.round = 0
        self.guys = guys

        for s in self.stats.values():
            s.next_game()
            s.build_decision_tree()
            # print '#################################################'
            # print '########            TREE for {}           ########'.format(s.name)
            # print '#################################################'
            # print s.tree
            # print

    def game_state(self):
        return tuple(g.state for g in self.guys.values())

    def round_result(self, actions):
        for i, action in enumerate(actions):
            stats = self.stats[i]

            if self.round > 0:
                stats.save_action(self.state, action)

            M = 2
            if 1 <= self.round <= M:
                idx = self.round - 1
                stats.first_moves[idx][action] += 1

        self.round += 1

    def preround(self):
        self.state = self.game_state()

    def game_over(self):
        self.game += 1

        alive = [g for g in self.guys.values() if g.alive]
        n = float(len(alive))
        if n > 0:
            for g in alive:
                g.stats.score += 1 / n
        else:
            # Breaks if someone dies in a stupid way, but close enough
            for g in self.guys.values():
                g.stats.score += 1. / 3

        print 'Kills:'
        for k, stat in self.stats.iteritems():
            kills = ', '.join(
                'Player[{}]: {}'.format(*val)
                for val in stat.kills.iteritems()
            )
            print 'Player {}: {}'.format(k, kills)

        print 'Score:'
        for k, stat in self.stats.iteritems():
            print 'Player {}: {:>7.2%}'.format(k, stat.score / self.game)

        print 'Prediction accuracy:'
        for k, stats in self.stats.iteritems():
            ok = stats.correct
            total = stats.moves
            if stats.moves > 0:
                acc = ok / float(total)
                print 'Player {}:  {} / {}   {:>7.2%}'.format(k, ok, total, acc)
            else:
                print 'Player {}: died in the first round'.format(k)

    def predict_rational(self, guy, o1, o2):
        armed = len([o for o in [o1, o2] if o.can_shoot])
        alive = len([o for o in [o1, o2] if o.alive])
        can_dodge = len([o for o in [o1, o2] if o.can_dodge])

        if alive == 1:
            alive_guy = o1 if o1.alive else o2
            dead_guy = o1 if o1.dead else o2

        if armed == 1:
            armed_guy = o1 if o1.can_shoot else o2
            armless_guy = o1 if o1.empty else o2

        if can_dodge == 1:
            dodge_guy = o1 if o1.can_dodge else o2
            cant_dodge_guy = o1 if not o1.can_dodge else o2

        if alive == 2:
            if guy.can_shoot:
                if armed == 2:
                    if guy.can_dodge:
                        if guy.can_load:
                            a = {
                                shoot(o1): 0.25,
                                shoot(o2): 0.25,
                                DODGE: 0.45,
                                LOAD: 0.05
                            }
                        else:
                            a = {
                                shoot(o1): 0.25,
                                shoot(o2): 0.25,
                                DODGE: 0.5,
                            }
                    else:
                        if guy.can_load:
                            a = {
                                shoot(o1): 0.48,
                                shoot(o2): 0.48,
                                LOAD: 0.04
                            }
                        else:
                            a = {
                                shoot(o1): 0.5,
                                shoot(o2): 0.5,
                            }

                elif armed == 1:
                    if guy.can_dodge:
                        if guy.can_load:
                            a = {
                                shoot(armed_guy): 0.45,
                                shoot(armless_guy): 0.35,
                                DODGE: 0.15,
                                LOAD: 0.05
                            }
                        else:
                            a = {
                                shoot(armed_guy): 0.45,
                                shoot(armless_guy): 0.35,
                                DODGE: 0.2,
                            }
                    else:
                        if guy.can_load:
                            a = {
                                shoot(armed_guy): 0.55,
                                shoot(armless_guy): 0.4,
                                LOAD: 0.05
                            }
                        else:
                            a = {
                                shoot(armed_guy): 0.6,
                                shoot(armless_guy): 0.4,
                            }
                else:
                    if can_dodge == 2:
                        if guy.can_load:
                            a = {
                                shoot(o1): 0.4,
                                shoot(o2): 0.4,
                                LOAD: 0.2
                            }
                        else:
                            a = {
                                shoot(o1): 0.5,
                                shoot(o2): 0.5,
                            }
                    elif can_dodge == 1:
                        a = {
                            shoot(dodge_guy): 0.6,
                            shoot(cant_dodge_guy): 0.4,
                        }
                    else:
                        a = {
                            shoot(o1): 0.5,
                            shoot(o2): 0.5,
                        }
            else:
                if armed == 2:
                    if guy.can_dodge:
                        a = {
                            DODGE: 0.85,
                            LOAD: 0.15
                        }
                    else:
                        a = always(LOAD)

                elif armed == 1:
                    if guy.can_dodge:
                        a = {
                            DODGE: 0.7,
                            LOAD: 0.3
                        }
                    else:
                        a = always(LOAD)
                else:
                    a = always(LOAD)

        elif alive == 1:
            if guy.can_shoot:
                if alive_guy.can_shoot:
                    if guy.can_dodge:
                        a = {
                            shoot(alive_guy): 0.5,
                            DODGE: 0.3,
                            LOAD: 0.2
                        }
                    else:
                        a = {
                            shoot(alive_guy): 0.8,
                            LOAD: 0.2
                        }
                else:
                    if alive_guy.can_dodge:
                        a = {
                            shoot(alive_guy): 0.6,
                            LOAD: 0.4
                        }
                    else:
                        a = always(shoot(alive_guy))
            else:
                if alive_guy.can_shoot:
                    if guy.can_dodge:
                        a = {
                            DODGE: 0.9,
                            LOAD: 0.1
                        }
                    else:
                        a = always(LOAD)
                else:
                    a = always(LOAD)

        return a

    def predict_by_reactions(self, guy):
        if self.state in guy.stats.reactions:
            print '-- Based on the state reactions:'

            moves = guy.stats.reactions[self.state]
            dist = dist_from_histogram(moves)

            e = entropy(dist)
            max_entropy = 2.0

            count = sum(moves.values())

            # best, count = max(moves.iteritems(), key=lambda x: x[1])
            # frac = count / float(total)
            # cf = 1 - 0.7 / total
            # power = frac * cf

            # print '{} matches, {:7.2%} consistentcy, {:.2} count factor'\
            #         .format(total, frac, cf)

            # distribution = {
            #     action: n / float(total)
            #     for action, n in moves.iteritems()
            # }
            # return (distribution, power)

            print 'Entropy: {} (max = {})'.format(e, max_entropy)

            size_factor = 1 - 0.7 / count
            print '{} records, sample size power = {:.3}'.format(count, size_factor)

            norm_e = 1 - e / max_entropy
            power = norm_e * size_factor
            print 'Total predictive power = {:.3}'.format(power)

            return (dist, power)
        else:
            return (None, None)

    def predict_by_past(self, guy):
        if self.game > 0 and 1 <= self.round <= 2:
            print '-- Based on the past initial rounds:'

            past = guy.stats.action_dist(self.state, self.round)
            dist = dist_from_histogram(past)
            dist = without(dist, DEAD)

            if not dist:
                return (None, None)

            e = entropy(dist)
            max_entropy = 2.0

            print 'Entropy: {} (max = {})'.format(e, max_entropy)

            n = self.game
            size_factor = 1 - 0.7 / n
            print '{} games, sample size power = {:.3}'.format(n, size_factor)

            norm_e = 1 - e / max_entropy
            power = norm_e * size_factor

            print 'Total predictive power = {:.3}'.format(power)

            return (dist, power)
        else:
            return (None, None)

    def predict_by_decision_tree(self, guy):
        if self.game > 0:
            print '-- Based on decision tree:'

            dist, size = search_tree(guy.stats.tree, self.state)

            n = self.game
            size_factor = 1 - 0.7 / n
            power = size_factor
            print 'sample size = {}'.format(n, size)
            print 'Total predictive power = {:.3}'.format(power)

            return (dist, power)
        else:
            return (None, None)

    def predict_one_guy(self, guy, o1, o2):
        if guy.dead:
            return always(DEAD)

        total = []

        a = self.predict_rational(guy, o1, o2)
        total.append((a, 0.1))

        past, w = self.predict_by_past(guy)
        if past:
            print_options(past)
            total.append((past, w))

        reactions, w = self.predict_by_reactions(guy)
        if reactions:
            print_options(reactions)
            total.append((reactions, w))

        decision, w = self.predict_by_decision_tree(guy)
        if decision:
            print_options(decision)
            total.append((decision, w))

        a = combine(*total)
        return self.clear(guy, o1, o2, a)

    def clear(self, guy, o1, o2, a):
        if guy.empty:
            a = without(a, shoot(o1))
            a = without(a, shoot(o2))
        if guy.dodged:
            a = without(a, DODGE)
        if guy.full:
            a = without(a, LOAD)
        a = without(a, DEAD)
        return a


class GameSimulator(object):
    def __init__(self, guys):
        self.guys = {g.name: copy(g) for g in guys}

    def simulate_move(self, actions):
        events = []

        for i, guy in self.guys.iteritems():
            action = actions[i]

            if action == DODGE:
                if guy.can_dodge:
                    guy.act_dodge()
                else:
                    guy.alive = False
            elif action == LOAD:
                if guy.can_load:
                    guy.act_load()
                else:
                    guy.alive = False
            elif action != DEAD:
                if not guy.empty:
                    guy.act_shoot()

                    idx = get_target(action)
                    a, g = actions[idx], self.guys[idx]

                    if a not in (DODGE, shoot(guy)):
                        g.alive = False
                        events.append(('death', (g, guy)))
                else:
                    guy.alive = False

        return events


class Player(Cowboy):
    def __init__(self):
        super(Cowboy, self).__init__()
        self.game = 0
        self.killed = 0
        self.predictor = Predictor()

        self.state_count = defaultdict(int)
        self.loss_by_state = defaultdict(int)

    @report_exc
    def name(self, name):
        self.name = name

        # self.stats = {
        #     n: CowboyStats(n)
        #     for n in xrange(3)
        #     if n != name
        # }

    @report_exc
    def start(self):
        self.reset()
        self.round = 0

        self.enemies = {
            n: Cowboy(name=n)
            for n in xrange(3)
            if n != self.name
            }

        guys = dict({self.name: self}, **self.enemies)
        self.predictor.next_game(guys)

        for guy in self.guys:
            guy.stats = self.predictor.stats[guy.name]

        self.stats = self.predictor.stats[self.name]
        self.states = []

    @property
    def guys(self):
        return self.enemies.values()

    @property
    def armed_guys(self):
        return [c for c in self.guys if c.can_shoot]

    @property
    def alive_guys(self):
        return [c for c in self.guys if c.alive]

    def random_guy(self):
        return choice(list(self.alive_guys))

    def shoot_random_guy(self):
        guy = self.random_guy()
        return shoot(guy)

    def predict_actions(self):
        g1, g2 = self.guys
        print 'First guy (id={}):'.format(g1.name)
        a1 = self.predictor.predict_one_guy(g1, g2, self)
        print 'Total:'
        print_options(a1)
        print 'Entropy:     {:7.5}'.format(entropy(a1))
        best, p = max(a1.iteritems(), key=lambda x: x[0])
        g1.predicted = best

        print 'Second guy (id={}):'.format(g2.name)
        a2 = self.predictor.predict_one_guy(g2, g1, self)
        print 'Total:'
        print_options(a2)
        print 'Entropy:     {:7.5}'.format(entropy(a2))
        best, p = max(a2.iteritems(), key=lambda x: x[0])
        g2.predicted = best

        return product(a1, a2)

    def decide(self):
        print 'Player {}:'.format(self.name)

        if self.round == 0:
            g1, g2 = self.guys
            g1.predicted = LOAD
            g2.predicted = LOAD
            return always(LOAD)

        todo = defaultdict(float)

        options = self.predict_actions()
        print 'Predictions: '
        print_options(options)

        print 'My own actions as predicted:'
        my = self.predictor.predict_one_guy(self, *self.guys)
        print 'Total:'
        print_options(my)
        print 'Entropy:     {:7.5}'.format(entropy(my))
        pred_best, p = max(my.iteritems(), key=lambda x: x[0])

        for option, p in options.iteritems():
            a0, a1 = option

            r = self.calculate_responses(p, a0, a1)
            for a, s in r.iteritems():
                todo[a] += s * p

        print 'Scores: '
        for a, s in todo.iteritems():
            print '  {:30} :  {:>3}'.format(a, s)

        best, score = max(todo.items(), key=lambda x: x[1])
        print 'Best choice: {} (score: {})'.format(best, score)

        if pred_best == best:
            self.stats.correct += 1
        self.stats.moves += 1
        return always(best)

    def other(self, guy):
        g1, g2 = self.guys
        return g1 if g1 is not guy else g2

    def available_actions(self):
        actions = []
        if self.can_load:
            actions.append(LOAD)
        if self.can_dodge:
            actions.append(DODGE)
        if self.can_shoot:
            for g in self.alive_guys:
                actions.append(shoot(g))
        return actions

    def calculate_responses(self, p, a0, a1):
        # print 'Calculate response for {}, {}'.format(a0, a1)
        # print '- - - - - - - - - - - - - - - - - - - - - -'

        g0, g1 = self.guys
        guys = [self, g0, g1]

        results = {}

        for a in self.available_actions():
            acts = [a, a0, a1]
            act_dict = {g.name: act for g, act in zip(guys, acts)}
            # print 'Actions: {}'.format(act_dict)

            game = GameSimulator(guys)
            me, cg0, cg1 = [game.guys[g.name] for g in guys]

            events = game.simulate_move(act_dict)
            # print 'Aftermatch: {}'.format(events)
            score = self.evaluate(me, [cg0, cg1])
            # print 'Score: {}'.format(score)
            results[a] = score

        # print 'Done!'
        pairs = results.items()
        shuffle(pairs)
        best, score = max(pairs, key=lambda x: x[1])
        # print 'Best choice: {} (score: {})'.format(best, score)
        return results

    def player_strength(self, guy):
        score = guy.stats.score / self.game if self.game > 0 else 0

        if self.killed > 0:
            killed_me = guy.stats.kills[self.name]
            kf = killed_me / float(self.killed)
            return 0.6 * kf + 0.4 * score
        else:
            return score

    def game_state(self, me, g0, g1):
        return (me.state, g0.state, g1.state)

    def evaluate(self, me, guys):
        # print 'Me:'
        # self.print_guy(me)
        # print 'Them:'
        # for g in guys:
        #     self.print_guy(g)

        g1, g2 = guys
        alive = [g for g in guys if g.alive]

        score = 0.0

        if me.dead:
            score -= 5 + 2 * self.killed / float(self.game + 1)

        elif len(alive) == 0:
            score += 5

        elif len(alive) == 2:
            clip_bonus = [0, 0.6, 1.0, 1.4][me.clip]
            score += clip_bonus

            if self.can_dodge:
                score += 1

            clip_penalties = [0, 0.5, 0.9, 1.3]
            score -= clip_penalties[g1.clip]
            score -= clip_penalties[g2.clip]
        else:
            enemy = alive[0]
            dead_one = g1 if enemy is g2 else g2

            score += 1.5 + 1.5 * self.player_strength(dead_one)

            def power(g):
                return g.clip if not g.empty else 1 if g.can_dodge else 0

            my_power = power(me)
            enemy_power = power(enemy)

            if me.clip > enemy_power:
                score += 2
            elif enemy.clip > my_power:
                score -= 2
            else:
                clip_bonus = [0, 1, 1.5, 2][me.clip]
                score += clip_bonus

                if self.can_dodge:
                    score += 0.6

        state = self.game_state(me, g1, g2)

        if state in self.state_count and state in self.loss_by_state:
            n = self.state_count[state]
            lost = self.loss_by_state[state]
            loss_perc = lost / float(n)

            if n > 5 and loss_perc > 0.8:
                score -= 1005

        return score

    @report_exc
    def preround_info(self, alive, bullets):
        for guy, i in self.enum_guys():
            guy.alive = alive[i]
            guy.clip = bullets[i]

        self.predictor.preround()

    @report_exc
    def round_result(self, actions):
        print 'After round'
        for guy, i in self.enum_guys():
            action = actions[i]
            guy.dodged = action == DODGE

            if guy.predicted == action:
                guy.stats.correct += 1
            guy.stats.moves += 1

        g0, g1 = self.guys
        guys = [self, g0, g1]

        acts = [actions[g.name] for g in guys]
        act_dict = {g.name: act for g, act in zip(guys, acts)}

        game = GameSimulator(guys)
        me, cg0, cg1 = [game.guys[g.name] for g in guys]

        events = game.simulate_move(act_dict)

        for what, args in events:
            if what == 'death':
                who, killer = args
                killer_stat = self.predictor.stats[killer.name]
                killer_stat.kills[who.name] += 1
                self.predictor.guys[who.name].alive = False

        self.predictor.round_result(actions)
        self.round += 1
        self.states.append(self.game_state(self, g0, g1))

    @report_exc
    def die(self):
        self.killed += 1
        for state in self.states:
            self.loss_by_state[state] += 1

    @report_exc
    def game_over(self, score):
        self.game += 1
        self.predictor.game_over()
        for state in self.states:
            self.state_count[state] += 1

    def enum_guys(self):
        for guy in self.guys:
            yield (guy, guy.name)

    # Technical details

    @report_exc
    def strategy(self):
        options = self.decide()
        action = choose(options)
        return self.perform_action(action)

    def perform_action(self, action):
        if action == DODGE:
            self.act_dodge()
        elif action == LOAD:
            self.act_load()
        else:
            self.act_shoot()
        return action
