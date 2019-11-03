import random
import partitions


class Game:
    def __init__(self, world):
        self.world = world
        self.coalitions = set()

    def play(self):
        for c in self.coalitions:
            agents = self.world.get_agents(c)
            results = {}
            for a in agents:
                results[a.id] = a.work()
            # Phase de notation: chaque agent note
            # ses pairs en fonction du resultat de la partie
            for a in agents:
                a.request_reviews(results)

    def all_partition_set(self):
        agents_ids = list(self.world.agents_index.keys())
        for p in partitions.generator(len(agents_ids)):
            res = [set() for _ in range(max(p))]
            for i in range(len(p)):
                res[p[i] - 1].add(agents_ids[i])
            yield set(frozenset(s) for s in res)

    def get_random_partition(self):
        partitions = self.all_partition_set()
        return random.choice(list(partitions))

    def get_partition_stable(self):
        reputations = self.world.get_reputations()
        partitions = self.all_partition_set()
        partition_stable = None
        for p in partitions:
            if self.is_stable(p, reputations):
                # On ignore la grande coalition et les petites
                if 1 < len(p) < len(self.world.agents):
                    partition_stable = p
        return partition_stable

    def get_preferences(self, partition, reputations):
        preferences = {}
        for a in self.world.agents:
            preferences[a.id] = a.request_preferences(partition, reputations)
        return preferences

    def is_stable(self, partition, reputations):
        raise NotImplementedError

    def print_party(self):
        string = "### GAME ####################################\nCoalitions:\t"
        for group in self.coalitions:
            string += "("
            for a_id in group:
                string += "{} ".format(a_id)
            string += ") "
        # Eigen
        string += "\nOrders:\nEigen Trust:\t"
        eigen_order = sorted(
            self.world.get_reputations().items(),
            key=lambda i: i[1]
        )
        for a_id, _ in eigen_order:
            string += "{} < ".format(a_id)
        string += "\nReliabilities:\t"
        reliability_order = sorted(
            ((a.id, a.reliability) for a in self.world.agents),
            key=lambda i: i[1]
        )
        # Agents' reliabilities
        for a_id, _ in reliability_order:
            string += "{} < ".format(a_id)
        # Success rate total of good interaction / total of interaction
        string += "\nSuccess rate:\t{}".format(self.world.get_success_rate())
        # Comparaison betwing reliability and eigen orders
        string += "\nGood placement:\t{}".format(
            sum(1 for i in range(len(self.world.agents))
                if reliability_order[i][0] == eigen_order[i][0])
        )
        string += "\n#############################################\n"
        print(string)


class NashGame(Game):
    def is_stable(self, partition, reputations):
        preferences = self.get_preferences(partition, reputations)
        for a_id, pref in preferences.items():
            if a_id not in pref[-1].group:
                return False
        return True


class ISGame(Game):
    def is_stable(self, partition, reputations):
        preferences = self.get_preferences(partition, reputations)
        for a_id, pref in preferences.items():
            if a_id not in pref[-1].group:
                for b_id in pref[-1].group:
                    # On regarde du point de vue de b
                    # Ce groupe pref[-1] n'est pas forcement son prefere
                    for b_pref in preferences[b_id]:
                        if b_pref.group == pref[-1].group:
                            if reputations[a_id] < b_pref.value:
                                return False
        return True


class ICSGame(Game):
    def is_stable(self, partition, reputations):
        preferences = self.get_preferences(partition, reputations)
        for a_id, pref in preferences.items():
            if a_id not in pref[-1].group:
                for b_id in pref[-1].group:
                    # On regarde du point de vue de b
                    # Ce groupe pref[-1] n'est pas forcement son prefere
                    for b_pref in preferences[b_id]:
                        if b_pref.group == pref[-1].group:
                            if reputations[a_id] < b_pref.value:
                                return False
                for a_pref in preferences[a_id]:
                    if a_id in a_pref.group:
                        for c_id in a_pref.group:
                            # On ignore a
                            if c_id == a_id:
                                continue
                            # On regarde du point de vue de c
                            for c_pref in preferences[c_id]:
                                if c_pref.group == pref[-1].group:
                                    if reputations[a_id] > c_pref.value:
                                        return False
        return True


GAME_TYPES = {
    'nash': NashGame,
    'is': ISGame,
    'ics': ICSGame,
}
