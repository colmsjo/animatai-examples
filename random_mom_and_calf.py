# pylint: disable=missing-docstring, global-statement, invalid-name, too-few-public-methods, no-self-use
#
# A random Mother cachelot and calf
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

import random

from ecosystem.agents import Agent
from gzutils.gzutils import DotDict, Logging

from sea import Sea, Song, Squid

# Setup logging
# =============

DEBUG_MODE = True
l = Logging('random_mom_and_calf', DEBUG_MODE)

# Mom that moves by random until squid is found. Move forward when there is
# squid and sing.
def mom_program(percept):

    # unpack the percepts tuple: ([Thing|NonSpatial], rewards)
    percepts, rewards = percept

    action = None
    for percept in percepts:
        object_, radius = percept
        if isinstance(object_, Squid):
            l.info('--- MOM FOUND SQUID, SINGING AND EATING! ---')
            action = 'sing_eat_and_forward'

    if not action:
        action = 'forward'
        rand = random.random()
        if rand < 1/3:
            action = 'dive_and_forward'
        elif rand < 2/3:
            action = 'up_and_forward'


    return action


# Calf that will by random until hearing song. Dive when hearing song.
# The world will not permit diving below the bottom surface, so it will
# just move forward.
def calf_program(percept):

    # unpack the percepts tuple: ([Thing|NonSpatial], rewards)
    percepts, rewards = percept

    action = None

    for percept in percepts:
        object_, radius = percept
        if isinstance(object_, Squid):
            l.info('--- CALF FOUND SQUID, EATING! ---')
            action = 'eat_and_forward'

        if not action and isinstance(object_, Song):
            l.info('--- CALF HEARD SONG, DIVING! ---')
            action = 'dive_and_forward'


    if not action:
        action = 'forward'
        rand = random.random()
        if  rand < 1/3:
            action = 'dive_and_forward'
        elif rand < 2/3:
            action = 'up_and_forward'

    return action


# Main
# =====

# left: (-1,0), right: (1,0), up: (0,-1), down: (0,1)
#MOVES = [(0, -1), (0, 1)]

terrain = ('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW\n' +
           'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')

# the mother and calf have separate and identical lanes
things = ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n' +
          '                                                  \n' +
          '  ss                                      ss      \n' +
          'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n' +
          '                                                  \n' +
          '  ss                                      ss      \n' +
          'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

# the mother and calf have separate and identical lanes
exogenous_things = ('                                                  \n' +
                    '                                                  \n' +
                    '                                   ss             \n' +
                    '                                                  \n' +
                    '                                                  \n' +
                    '                                   ss             \n' +
                    '                                                  ')


mom_start_pos = (0, 1)
calf_start_pos = (0, 4)

# `motors` can perform several `actions`. The Sea Environment has four available
# `actions`: `eat`, `down`, `up`, `forward`. There is also one `nsaction` which is `sing`
# `sensors` are boolean variables indicating percepts (`Things` of different kinds)
# that are perceived. Active `sensors` are sent as input to the `program`
OPTIONS = DotDict({
    'terrain': terrain.split('\n'),
    'things': things.split('\n'),
    'exogenous_things': exogenous_things.split('\n'),
    'exogenous_things_prob': 0.01,
    'objectives': {'energy': 1.0},
    'rewards':{
        'sing_eat_and_forward': {
            Squid: {
                'energy': 0.1
            },
            None: {
                'energy': -0.05
            }
        },
        'eat_and_forward': {
            Squid: {
                'energy': 0.1
            },
            None: {
                'energy': -0.05
            }
        },
        'dive_and_forward': {
            None: {
                'energy': -0.002
            }
        },
        'up_and_forward': {
            None: {
                'energy': -0.002
            }
        },
        'forward': {
            None: {
                'energy': -0.001
            }
        },
    },
    'wss_cfg': {
        'numTilesPerSquare': (1, 1),
        'drawGrid': True,
        'randomTerrain': 0,
        'agents': {
            'mom': {
                'name': 'M',
                'pos': mom_start_pos,
                'hidden': False
            },
            'calf': {
                'name': 'c',
                'pos': calf_start_pos,
                'hidden': False
            }
        }
    }
})


# Main
# =====

def run(wss=None, steps=None, seed=None):
    l.debug('Running random_mom_and_calf in', str(steps), 'steps with seed', seed)
    steps = int(steps) if steps else 10

    random.seed(seed)

    options = OPTIONS
    options.wss = wss
    sea = Sea(options)

    mom = Agent(mom_program, 'mom')
    calf = Agent(calf_program, 'calf')

    sea.add_thing(mom, mom_start_pos)
    sea.add_thing(calf, calf_start_pos)

    sea.run(steps)

if __name__ == "__main__":
    run()
