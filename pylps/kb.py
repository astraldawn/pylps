'''
Class for the knowledge base
'''
from ordered_set import OrderedSet
from pylps.constants import *
from pylps.kb_objects import Causality, MultiGoal


class _KB(object):
    causalities = {}
    facts = {}
    fluents = {}
    reactive_rules = []

    _clauses = []
    _goals = OrderedSet()
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

        if fluent in self.fluents[fluent.name]:
            return False

        self.fluents[fluent.name].add(fluent)
        return True

    def exists_fluent(self, fluent):
        try:
            return fluent in self.fluents[fluent.name]
        except KeyError:
            return False

    def remove_fluent(self, fluent):

        if not self.fluents[fluent.name]:
            self.fluents[fluent.name] = set()

        try:
            self.fluents[fluent.name].remove(fluent)
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
        self._goals.add(MultiGoal(goals))

    def remove_goals(self, goals):
        try:
            self._goals.remove(MultiGoal(goals))
        except KeyError:
            pass

    def reset_goals(self):
        self._goals = OrderedSet()

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

    def add_causality_outcome(self, action, fluent, causality_type):
        if action.name not in self.causalities:
            self.causalities[action.name] = Causality(action)

        self.causalities[action.name].add_outcome(
            [causality_type, fluent])

    def add_causality_constraint(self, action, fluents):
        if action.name not in self.causalities:
            self.causalities[action.name] = Causality(action)

        self.causalities[action.name].add_constraint(fluents)

    def add_causality_req(self, action, items):
        if action.name not in self.causalities:
            self.causalities[action.name] = Causality(action)

        self.causalities[action.name].add_req(items)

    def exists_causality(self, action):
        try:
            return self.causalities[action.name]
        except KeyError:
            return False

    def show_causalities(self):
        for action_name, causality in self.causalities.items():
            print(causality)

    ''' Observations '''

    @property
    def observations(self):
        return self._observations

    def add_observation(self, observation):
        self._observations.append(observation)

    ''' Facts '''

    def add_fact(self, fact):
        if fact.name not in self.facts:
            self.facts[fact.name] = OrderedSet()

        # Does it contain a variable?
        contains_var = False
        for arg in fact.args:
            try:
                if arg.BaseClass == VARIABLE:
                    contains_var = True
            except AttributeError:
                pass

        # Do not save facts that are not grounded
        if contains_var:
            return

        self.facts[fact.name].add(fact)

    def exists_fact(self, fact):
        try:
            facts = self.facts[fact.name]
            return fact in facts
        except KeyError:
            return False

    def get_facts(self, fact):
        try:
            return self.facts[fact.name]
        except KeyError:
            return []

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
