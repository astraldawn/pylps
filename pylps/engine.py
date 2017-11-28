from pylps.constants import *
from pylps.kb import KB
from pylps.unifier import unify_conds, reify_goals, unify_goal


class _ENGINE(object):
    start_time = 1
    current_time = 1
    max_time = 5

    def set_params(self, max_time):
        self.max_time = max_time

    def run(self):
        self.current_time = self.start_time
        KB.reset_goals()

        while self.current_time <= self.max_time:
            self._check_rules()
            self._check_goals()

            self.current_time += 1

    def _check_rules(self):
        # Check rules
        for rule in KB.rules:
            # Check conditions of the rules
            substitution = unify_conds(rule.conds, self.current_time)

            # If there is no substitution, go to the next rule
            if not substitution:
                continue

            new_goals = reify_goals(rule.goals, substitution)
            KB.add_goals(new_goals)

    def _check_goals(self):
        '''
        Work through the goals individually
        '''
        for goal in KB.goals:
            # Check if the goal exists and attempt to add in a time
            unify_goal(goal, self.current_time)


ENGINE = _ENGINE()
