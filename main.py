import click

import random
import numpy as np
import signal

from world import World
from agent import AgentFactory, Agent
import game


def exit_handler(sig, frame):
    global run
    run = False


@click.command()
@click.option('--seed', type=int)
@click.argument('agents-number', type=int)
@click.argument('reviews-method')
@click.argument('preferences-method')
@click.argument('game-type')
def play(seed, agents_number, reviews_method, preferences_method, game_type):
    global run
    run = True

    # Settings ################################################################
    if seed:
        random.seed(seed)
        np.random.seed(seed)

    np.set_printoptions(precision=4)

    # Inputs Checks ###########################################################
    if agents_number < 3:
        print("At least three agents are required")
        return

    if reviews_method not in Agent.REVIEWS_METHODS:
        print("{} is not implemented. Choose from {}"
              .format(reviews_method, Agent.REVIEWS_METHODS))
        return

    if preferences_method not in Agent.PREFERENCES_METHODS:
        print("{} is not implemented. Choose from {}"
              .format(preferences_method, Agent.REVIEWS_METHODS))
        return

    if game_type not in game.GAME_TYPES:
        print("{} is not implemented. Choose from {}"
              .format(game_type, game.GAME_TYPES.keys()))
        return

    # Intialisation ###########################################################
    w = World()
    g = game.GAME_TYPES[game_type](w)

    f = AgentFactory(reviews_method, preferences_method)
    w.add_agents(*f.create(agents_number))
    w.fetch_reviews()  # Initialize reviews matrix

    signal.signal(signal.SIGINT, exit_handler)

    # Main Loop ###############################################################
    while run:
        g.coalitions = g.get_partition_stable()
        if g.coalitions is None:
            run = False
        g.play()
        g.print_party()
        w.fetch_reviews()

    # End #####################################################################
    print("Game Over !")
    print(w.reviews)
    print(w.normalize_reviews())
    print(w.get_reputations())
    print(dict((a.id, a.reliability) for a in w.agents))


if __name__ == "__main__":
    play()
