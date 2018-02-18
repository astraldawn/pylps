from pylps.kb import KB
from pylps.unifier import unify_conds, reify_goals, unify_obs
from pylps.solver import SOLVER
from pylps.solver_utils import process_solutions


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
            self._check_rules()
            self._check_goals()

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
                new_goals = reify_goals(rule.goals, substitution, defer=True)
                KB.add_goals(new_goals, substitution)

    def _check_goals(self):

        solutions = SOLVER.solve_goals(self.current_time)
        process_solutions(solutions, self.current_time)


ENGINE = _ENGINE()
