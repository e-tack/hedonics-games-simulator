import numpy as np
from collections import OrderedDict


class World:
    def __init__(self):
        self._agents = []
        self._agents_index = OrderedDict()
        self._reviews = np.array([])

    @property
    def agents(self):
        return self._agents

    @property
    def agents_index(self):
        return self._agents_index

    def get_agent(self, a_id):
        x = self.agents_index.get(a_id)
        if x is not None:
            return self.agents[x]

    def get_agents(self, coalition):
        res = []
        for a_id in self.agents_index.keys():
            if a_id in coalition:
                res.append(self.agents[self.agents_index[a_id]])
        return res

    def add_agents(self, *agents):
        for a in agents:
            self.agents_index[a.id] = len(self.agents)
            self.agents.append(a)

    @property
    def reviews(self):
        return self._reviews

    def fetch_reviews(self):
        n = len(self.agents)
        res = np.zeros((n, n))
        for a in self.agents:
            for b_id in a.reviews:
                a_index = self.agents_index[a.id]
                b_index = self.agents_index[b_id]
                res[a_index, b_index] = \
                    a.reviews[b_id].good - a.reviews[b_id].bad
        self._reviews = res

    def normalize_reviews(self):
        shape = self.reviews.shape
        res = np.zeros(shape)
        for i in range(shape[0]):
            s = sum([max(x, 0) for x in self.reviews[i, :]])
            if s != 0:
                for j in range(shape[0]):
                    res[i, j] = max(self.reviews[i, j], 0) / s
            else:
                res[i, :] = 1 / (shape[0] - 1)
                res[i, i] = 0
        return res

    def get_reputations(self, alpha=0.001, epsilon=0.001):
        """ Eigen Thrust """
        normalized = self.normalize_reviews()
        size = normalized.shape[0]
        r = np.full(size, 1 / size)
        p = np.full(size, 1 / size)
        while True:
            t = np.dot(normalized.T, r)
            t = np.dot(1 - alpha, t) + np.dot(alpha, p)
            delta = np.linalg.norm(t - r)
            if delta < epsilon:
                res = {}
                agents_keys = dict(  # Reverse keys and values
                    (v, k) for k, v in self.agents_index.items()
                )
                for i in range(len(t)):
                    res[agents_keys[i]] = t[i]
                return res
            r = t

    def get_success_rate(self):
        good = 0
        bad = 0
        for a in self.agents:
            for b_id in a.reviews:
                good += a.reviews[b_id].good
                bad += a.reviews[b_id].bad
        if good + bad == 0:
            return 0
        return good / (good + bad)
