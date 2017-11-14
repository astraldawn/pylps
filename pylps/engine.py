from pylps.constants import *
from pylps.kb import KB
from pylps.unifier import unify_conds, unify_goals


class _ENGINE(object):
    current_time = 0
    max_time = 5
    observations = {}

    def set_params(self, max_time):
        self.max_time = max_time

    def run(self):
        while self.current_time < self.max_time:
            cur_time = self.current_time

            # Update Observations
            # self._update_observations()
            # self._show_observations(cur_time)

            # Check rules
            for rule in KB.rules:
                # Check conditions of the rules
                substitution = unify_conds(rule.conds, cur_time)

                # If there is no substitution, go to the next rule
                if not substitution:
                    continue

                new_goals = unify_goals(rule.goals, substitution)

            self.current_time += 1

    # def _update_observations(self):
    #     cur_time = self.current_time

    #     # Fluents
    #     self.observations[FLUENT] = set()
    #     for fluent in KB.fluents:
    #         if fluent.state:
    #             self.observations[FLUENT].add((
    #                 FLUENT, fluent.name,
    #                 ((CONSTANT, cur_time),)
    #             ))

    # def _show_observations(self, time=None):
    #     print('-----\nObservations at time %s' % time)
    #     for k, v in self.observations.items():
    #         print(k, v)
    #     print('-----')


ENGINE = _ENGINE()
