from random import random
from collections import namedtuple


def _int_id_generator():
    id = 0
    while True:
        yield id
        id += 1


Review = namedtuple('Review', 'good bad')
Preference = namedtuple('Preference', 'group value')


class Agent:
    def __init__(self, reliability, reviews_method, preferences_method,
                 id_generator=_int_id_generator()):
        # Identifiant unique
        self._id = next(id_generator)
        # Fiabilité du travail entre 0 et 1
        self._reliability = reliability
        # Notation a propos des autres agents
        # (note positive, note negative)
        self._reviews = {}
        # Choix de la methode de notation
        self._reviews_method = reviews_method
        # Choix de la methode de preferences
        self._preferences_method = preferences_method

    @property
    def id(self):
        return self._id

    @property
    def reliability(self):
        return self._reliability

    # Reviews Methods  ########################################################
    @property
    def reviews(self):
        return self._reviews

    def review(self, a_id, note):
        result = self.reviews.get(a_id, Review(0, 0))
        if note >= 0:
            result = Review(result.good + note, result.bad)
        else:
            result = Review(result.good, result.bad + abs(note))
        self._reviews[a_id] = result

    def _pessimist_reviews(self, game_results):
        success = all((
            result[1] for result
            in game_results.items()
            if result[0] != self.id
        ) or [0])
        for a_id in game_results.keys():
            if a_id == self.id:
                continue
            if success:
                self.review(a_id, +1)
            else:
                self.review(a_id, -1)

    def _optimist_reviews(self, game_results):
        success = any((
            result[1] for result
            in game_results.items()
            if result[0] != self.id
        ) or [0])
        for a_id in game_results:
            if a_id == self.id:
                continue
            if success:
                self.review(a_id, +1)
            else:
                self.review(a_id, -1)

    def request_reviews(self, game_results):
        if self._reviews_method == 'pessimist':
            return self._pessimist_reviews(game_results)
        if self._reviews_method == 'optimist':
            return self._optimist_reviews(game_results)
        raise NotImplementedError

    REVIEWS_METHODS = ['pessimist', 'optimist']

    # Preferences  ############################################################
    def _average_preferences(self, coalition, reputations):
        means = {}
        for group in coalition:
            if len(group) > 1:
                means[group] = sum(reputations[a_id]
                                   for a_id in group
                                   if a_id != self.id)
                means[group] /= len(group) - 1
            else:
                # Si l'agent est tout seul
                means[group] = 0
        return means

    def _min_preferences(self, coalition, reputations):
        means = {}
        for group in coalition:
            if len(group) > 1:
                means[group] = min(reputations[a_id]
                                   for a_id in group
                                   if a_id != self.id)
                means[group] /= len(group) - 1
            else:
                means[group] = 0
        return means

    def _max_preferences(self, coalition, reputations):
        means = {}
        for group in coalition:
            if len(group) > 1:
                means[group] = max(reputations[a_id]
                                   for a_id in group
                                   if a_id != self.id)
                means[group] /= len(group) - 1
            else:
                means[group] = 0
        return means

    def request_preferences(self, coalition, reputations):
        means = {}
        if self._preferences_method == 'average':
            means = self._average_preferences(coalition, reputations)
        elif self._preferences_method == 'minimum':
            means = self._min_preferences(coalition, reputations)
        elif self._preferences_method == 'maximum':
            means = self._max_preferences(coalition, reputations)
        else:
            raise NotImplementedError
        return sorted(
            map(lambda item: Preference(*item), means.items()),
            key=lambda p: p.value
        )

    PREFERENCES_METHODS = ['average', 'minimum', 'maximum']

    # Work simulation  ########################################################
    def work(self):
        """returns True if work has been done right"""
        return random() <= self.reliability


class AgentFactory:
    def __init__(self, reviews_method, preferences_method):
        self.reviews_method = reviews_method
        self.preferences_method = preferences_method

    def create(self, n=1):
        return [Agent(
            random(),
            self.reviews_method,
            self.preferences_method
        ) for _ in range(n)]


if __name__ == "__main__":
    a = Agent(0.5, 'optimist', 'average')
    coalition = set([
        frozenset([0, 1, 2]),
        frozenset([3]),
    ])
    reputations = {
        0: 0.1,
        1: 0.1,
        2: 0.1,
        3: 0.7,
    }
    print(a.request_preferences(coalition, reputations))
