from pylps.constants import *
from pylps.kb import KB
from pylps.unifier import unify_conds, reify_goals, unify_obs, \
    unify_multigoal


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
            self._check_observations()
            self._check_goals()
            self._check_rules()

            self.current_time += 1

    def _check_observations(self):
        for observation in KB.observations:
            if observation.end == self.current_time:
                # Unify with the KB?
                unify_obs(observation)

    def _check_rules(self):
        # Check rules
        for rule in KB.rules:
            # Check conditions of the rules
            substitutions = unify_conds(rule.conds, self.current_time)

            # If there are no substitutions, go to the next rule
            if not substitutions:
                continue

            for substitution in substitutions:
                new_goals = reify_goals(rule.goals, substitution)
                KB.add_goals(new_goals)

    def _check_goals(self):
        '''
        Work through the goals individually
        '''
        solved_goals = set()

        for multigoal in KB.goals:
            # Check if the goal exists and attempt to add in a time
            # print(multigoal)
            if unify_multigoal(multigoal, self.current_time):
                    solved_goals.add(multigoal)

        KB.remove_goals(solved_goals)


ENGINE = _ENGINE()
