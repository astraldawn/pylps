'''
Class for the knowledge base
'''
from pylps.constants import *


class _KB(object):
    causalities = []
    clauses = []
    fluents = {}
    reactive_rules = []

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

    def check_fluent(self, fluent):
        try:
            return fluent.to_tuple in self.fluents[fluent.name]
        except KeyError:
            return False

    def get_fluents(self, fluent):
        try:
            return self.fluents[fluent.name]
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

    ''' Others '''

    def add_clause(self, clause):
        self.clauses.append(clause)

    def add_causality(self, causality):
        self.causalities.append(causality)

    def show_clauses(self):
        for clause in self.clauses:
            print(clause)


KB = _KB()
