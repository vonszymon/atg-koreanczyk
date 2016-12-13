from game import *
from itertools import *
from random import *

games_to_play = 10000

all_players = [
    "agg03",
    "blaszczyk",
    "chorazyk",
    "czarnota",
    "figiela",
    "franczyk",
    "grajewski",
    "gruszka",
    "jurkowski",
    "kaczmarczyk",
    "Kudas",
    "lasak",
    "loza",
    "matrejek",
    "mlos",
    "mmazur",
    "ociepka",
    "opiola",
    "orzechowski",
    "pazik",
    "polnik",
    "rnd",
    "sikora",
    "skiba",
    "sliwa",
    "sokol",
    "tlos",
    "walaszewska",
    "wilaszek",
    "ymachkivskiy"
]

seed()

score = {}
games_played = {}
for x in all_players:
    score[x] = 0.0
    games_played[x] = 0

for x in all_players:
    for y in all_players:
        for z in all_players:
            if x != y and x != z and y != z:
                try:
                    s = games([x, y, z])
                    score[x] += s[0]
                    score[y] += s[1]
                    score[z] += s[2]
                    games_played[x] += GAMES_TO_PLAY
                    games_played[y] += GAMES_TO_PLAY
                    games_played[z] += GAMES_TO_PLAY

                except:
                    print "VERY VERY VERY BAD! Some exception"

for x in all_players:
    #  print x, "\t-->\t", score[x]
    print x, "\t-->\t", float(score[x]) / float(games_played[x])
