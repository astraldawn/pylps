'''
Class for the knowledge base
'''
from ordered_set import OrderedSet
from pylps.constants import *
from pylps.utils import *
from pylps.kb_objects import Causality, MultiGoal


class _KB(object):
    causalities = {}
    facts = {}
    fluents = {}
    reactive_rules = []

    _clauses = {}
    _goals = OrderedSet()
    _observations = []
    _constraints = []
    _fact_used_reactive = set()

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

    def add_goals(self, goals, subs):
        self._goals.add(MultiGoal(goals, subs))

    def remove_goals(self, goals):
        new_goals = OrderedSet()
        for goal in self._goals:
            if goal not in goals:
                new_goals.add(goal)
        self._goals = new_goals

    def reset_goals(self):
        self._goals = OrderedSet()

    ''' Clauses '''

    @property
    def clauses(self):
        return self._clauses

    def add_clause(self, clause):
        try:
            self._clauses[clause.name].add(clause)
        except KeyError:
            self._clauses[clause.name] = OrderedSet()
            self._clauses[clause.name].add(clause)

    def get_clauses(self, goal_object):
        return self._clauses.get(goal_object.name, [])

    def show_clauses(self):
        for name, clause in self._clauses.items():
            print(clause)

    ''' Causality '''

    def add_causality_outcome(self, action, fluent, causality_type):
        if action.name not in self.causalities:
            self.causalities[action.name] = Causality(action)

        self.causalities[action.name].add_outcome(
            [causality_type, fluent])

    def add_causality_req(self, action, items):
        if action.name not in self.causalities:
            self.causalities[action.name] = Causality(action)

        self.causalities[action.name].add_req(items)

    def exists_causality(self, action):
        return self.causalities.get(action.name, False)

    def show_causalities(self):
        for action_name, causality in self.causalities.items():
            print(causality)

    ''' Observations '''

    @property
    def observations(self):
        return self._observations

    def add_observation(self, observation):
        self._observations.append(observation)

    ''' Constraints '''

    @property
    def constraints(self):
        return self._constraints

    def add_constraint(self, constraint):
        self._constraints.append(constraint)

    def get_constraints(self, action):
        relevant_constraints = []
        for constraint in self._constraints:
            if (action, True) in constraint:
                relevant_constraints.append(constraint)
        return relevant_constraints

    def show_constraints(self):
        for constraint in self._constraints:
            print(constraint)

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

    def get_facts(self, fact, reactive_rule=False):
        try:
            facts = self.facts[fact.name]

            if not reactive_rule:
                return facts

            # Check if a fact was used to trigger a reactive rule
            if fact.name in self._fact_used_reactive:
                return []

            self._fact_used_reactive.add(fact.name)
            return facts
        except KeyError:
            return []

    def show_facts(self):
        for _, fact in self.facts.items():
            print(fact)

    ''' Logs '''

    def log_action(self, goal, subs):
        action = goal.obj
        action_args = reify_args(action.args, subs)
        goal_temporal_vars = reify(goal.temporal_vars, subs)
        self.log.append([ACTION, action.name, action_args, goal_temporal_vars])

    def log_action_obs(self, action, temporal_vars):
        self.log.append([ACTION, action.name, action.args, temporal_vars])

    def log_fluent(self, fluent, time, action_type):
        self.log.append([action_type, fluent.name, fluent.args, time])

    def show_log(self):
        for item in self.log:
            print(item)


KB = _KB()
