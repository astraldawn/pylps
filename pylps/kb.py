'''
Class for the knowledge base
'''
from ordered_set import OrderedSet
from pylps.constants import *
from pylps.utils import *
from pylps.kb_objects import *
from pylps.state import State


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
    _cycle_obs = OrderedSet()

    log = []

    ''' Rule controls '''

    @property
    def rules(self):
        return self.reactive_rules

    def add_rule(self, rule):
        self.reactive_rules.append(rule)

    def show_reactive_rules(self):
        for rule in self.reactive_rules:
            display(rule)

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

    def get_fluents(self, fluent):
        ret = []
        if not self.fluents.get(fluent.name):
            return ret

        for kb_fluent in self.fluents[fluent.name]:
            if len(kb_fluent.args) == len(fluent.args):
                ret.append(kb_fluent)

        return ret

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
            display(fluent)

    ''' Goal control '''

    @property
    def goals(self):
        return self._goals

    def add_goals(self, goals, subs):
        self._goals.add(State(goals, subs, from_reactive=True))

    def set_goals(self, goals):
        self._goals = goals

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
            display(clause)

    ''' Causality '''

    def add_causality_outcome(self, action, fluent, outcome):
        if action.name not in self.causalities:
            self.causalities[action.name] = Causality(action)

        self.causalities[action.name].add_outcome(
            CausalityOutcome(
                fluent=fluent,
                outcome=outcome
            ))

    def add_causality_req(self, action, items):
        if action.name not in self.causalities:
            self.causalities[action.name] = Causality(action)

        self.causalities[action.name].add_req(items)

    def exists_causality(self, action):
        return self.causalities.get(action.name, False)

    def show_causalities(self):
        for action_name, causality in self.causalities.items():
            display(causality)

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
        constraint = [
            Constraint(indiv_con[0], indiv_con[1])
            for indiv_con in constraint
        ]
        self._constraints.append(constraint)

    def get_constraints(self, action):
        relevant_constraints = []

        # TODO: Can this be made more efficient?
        for constraint in self._constraints:
            relevant = False
            for indiv_con in constraint:
                if relevant:
                    continue

                obj = indiv_con.goal

                try:
                    if obj.name == action.name:
                        relevant = True
                except AttributeError:
                    pass

            if relevant:
                relevant_constraints.append(constraint)
        return relevant_constraints

    def show_constraints(self):
        for constraint in self._constraints:
            display(constraint)

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
                return self._match_facts(fact, facts)

            # Check if a fact was used to trigger a reactive rule
            # Only check if it is being called to trigger a reactive rule
            if fact.name in self._fact_used_reactive:
                return []

            self._fact_used_reactive.add(fact.name)
            return self._match_facts(fact, facts)
        except KeyError:
            return []

    def _match_facts(self, fact, facts):
        '''
        Matches facts against the KB
        '''
        ret_facts = []
        for kb_fact in facts:
            arg_match = True
            for fact_arg, kb_fact_arg in zip(fact.args, kb_fact.args):
                if not arg_match:
                    continue

                try:
                    if fact_arg.BaseClass == VARIABLE:
                        continue
                except AttributeError:
                    if fact_arg != kb_fact_arg:
                        arg_match = False

            if arg_match:
                # ret_facts.append(kb_fact)
                yield kb_fact

        return ret_facts

    def show_facts(self):
        for _, fact in self.facts.items():
            display(fact)

    ''' Cycle actions '''

    @property
    def cycle_obs(self):
        return self._cycle_obs

    def add_cycle_obs(self, observation):
        self._cycle_obs.add(observation)

    def clear_cycle_obs(self):
        self._cycle_obs = OrderedSet()

    # @property
    # def cycle_actions(self):
    #     return self._goals.actions

    # def add_cycle_action(self, goal, subs):
    #     action = goal.obj
    #     action_args = reify_args(action.args, subs)
    #     goal_temporal_vars = reify(goal.temporal_vars, subs)
    #     action.args = action_args

    #     # self._cycle_actions.add((action, goal_temporal_vars))
    #     goal.add_action((action, goal_temporal_vars), propagate=True)
    #     # self.log_action(action.name, action_args, goal_temporal_vars)

    # def clear_cycle_actions(self):
    #     KB.goals.clear_actions()

    # def display_cycle_actions(self):
    #     display('\nCYCLE ACTIONS\n')
    #     for (cycle_action, temporal_vars) in self.cycle_actions:
    #         display(cycle_action, temporal_vars)
    #     display('\n')

    # def exists_cycle_action(self, action):
    #     return action in [action for (action, _) in self.cycle_actions]

    # def get_cycle_actions(self, action):
    #     ret = []
    #     for (cycle_action, temporal_vars) in self.cycle_actions:
    #         if cycle_action.name == action.name:
    #             ret.append(cycle_action)
    #     return ret

    ''' Logs '''

    def log_action(self, action, temporal_vars, from_obs=False):
        self.log.append(
            [action.BaseClass, action.name, action.args, temporal_vars,
             from_obs])

    def log_action_new(self, action, from_obs=False):
        converted_args = []

        # Argument conversion for final display
        for arg in action.args:
            try:
                if arg.BaseClass is LIST:
                    converted_args.append(arg.to_python())
                    continue
                if arg.BaseClass is CONSTANT:
                    converted_args.append(arg.const)
                    continue
            except AttributeError:
                pass

            converted_args.append(arg)

        self.log.append(
            [action.BaseClass, action.name, converted_args,
             (action.start_time, action.end_time), from_obs])

    def log_fluent(self, fluent, time, action_type):
        converted_args = []

        # Argument conversion for final display
        for arg in fluent.args:
            try:
                if arg.BaseClass is LIST:
                    converted_args.append(arg.to_python())
                    continue
                if arg.BaseClass is CONSTANT:
                    converted_args.append(arg.const)
                    continue
            except AttributeError:
                pass

            converted_args.append(arg)

        self.log.append([action_type, fluent.name,
                         converted_args, time, False])

    def show_log(self, show_events=False):
        for item in self.log:
            # Override to always show observation
            if item[4]:
                display(item[:4])
                continue

            if item[0] is EVENT and not show_events:
                continue
            display(item[:4])


KB = _KB()
