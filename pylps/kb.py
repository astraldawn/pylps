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
        fluent_tuple = (
            FLUENT, fluent.name,
            tuple(arg for arg in fluent.args)
        )
        self.fluents[fluent.name] = fluent_tuple

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
