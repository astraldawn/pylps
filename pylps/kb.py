'''
Class for the knowledge base
'''
from pylps.constants import *


class _KB(object):
    causalities = {}
    facts = {}
    fluents = {}
    reactive_rules = []

    _clauses = []
    _goals = set()
    _observations = []

    log = []

    ''' Rule controls '''

    @property
    def rules(self):
        return self.reactive_rules

    def add_rule(self, rule):
        self.reactive_rules.append(rule)

    def show_reactive_rules(self):
        for rule in self.reactive_rules:
            print(rule)

    ''' Fluent control '''

    def add_fluent(self, fluent):
        if fluent.name not in self.fluents:
            self.fluents[fluent.name] = set()

        self.fluents[fluent.name].add(fluent.to_tuple())

    def exists_fluent(self, fluent):
        try:
            return fluent.to_tuple() in self.fluents[fluent.name]
        except KeyError:
            return False

    def remove_fluent(self, fluent):

        if not self.fluents[fluent.name]:
            self.fluents[fluent.name] = set()

        try:
            self.fluents[fluent.name].remove(fluent.to_tuple())
        except KeyError:
            # Fluent removal fails
            return False

        return True

    def show_fluents(self):
        for _, fluent in self.fluents.items():
            print(fluent)

    ''' Goal control '''

    @property
    def goals(self):
        return self._goals

    def add_goals(self, goals):
        self._goals.update(goals)

    def remove_goals(self, goals):
        self._goals = self._goals - goals

    def reset_goals(self):
        self._goals = set()

    ''' Clauses '''

    @property
    def clauses(self):
        return self._clauses

    def add_clause(self, clause):
        self._clauses.append(clause)

    def show_clauses(self):
        for clause in self._clauses:
            print(clause)

    ''' Causality '''

    def add_causality(self, action, fluent, causality_type):
        if action.name not in self.causalities:
            self.causalities[action.name] = []

        self.causalities[action.name].append([causality_type, fluent])

    def exists_causality(self, action):
        try:
            return self.causalities[action.name]
        except KeyError:
            return False

    ''' Observations '''

    @property
    def observations(self):
        return self._observations

    def add_observation(self, observation):
        self._observations.append(observation)

    ''' Facts '''

    def add_fact(self, fact):
        if fact.name not in self.facts:
            self.facts[fact.name] = set()

        self.facts[fact.name].add(fact.to_tuple())

    def show_facts(self):
        for _, fact in self.facts.items():
            print(fact)

    ''' Logs '''

    def log_action(self, action, temporal_vars):
        self.log.append([ACTION, action.name, action.args, temporal_vars])

    def log_fluent(self, fluent, time, action_type):
        self.log.append([action_type, fluent.name, fluent.args, time])

    def show_log(self):
        for item in self.log:
            print(item)


KB = _KB()
