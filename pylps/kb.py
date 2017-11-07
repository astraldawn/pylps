'''
Class for the knowledge base
'''


class _KB(object):
    causalities = []
    clauses = []
    _fluents = {}
    fluents = []
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
        self._fluents[fluent.name] = fluent
        self.fluents.append(fluent)

    def modify_fluent(self, fluent_name, new_state):
        self._fluents[fluent_name].set_state(new_state)

    def show_fluents(self):
        for _, fluent in self._fluents.items():
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
