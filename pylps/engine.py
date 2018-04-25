import copy

from pylps.utils import *

from pylps.kb import KB
from pylps.unifier import unify_conds, reify_goals, unify_obs
from pylps.solver import SOLVER
from pylps.solver_utils import process_solutions
from pylps.state import State


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

            KB.clear_cycle_obs()

            self.current_time += 1

    def _check_observations(self):
        for observation in KB.observations:
            if observation.end_time == self.current_time:
                # Unify with the KB?
                unify_obs(observation)

    def _check_rules(self):
        # Check rules
        for rule in KB.rules:

            # Handle triggering from constant
            if rule.constant_trigger:
                continue

            conds = []
            true_trigger = False

            for cond in rule.conds:
                cond_object = copy.deepcopy(cond)
                rename_args(0, cond_object)
                conds.append(cond_object)

            # Special case for rules beginning with True
            if len(conds) == 1 and conds[0].BaseClass is CONSTANT and \
                    conds[0].const is True:
                true_trigger = True
                rule._constant_trigger = True
                substitutions = [{}]

            if not true_trigger:

                subs_list = list(SOLVER.backtrack_solve(
                    start=State(copy.deepcopy(conds), {}),
                    reactive=True,
                    current_time=self.current_time
                ))

                substitutions = [s.subs for s in subs_list]

            # print(true_trigger, conds, substitutions, self.current_time)

            if not substitutions:
                continue

            for substitution in substitutions:
                if substitution == {} and not true_trigger:
                    continue

                new_goals = reify_goals(rule.goals, substitution)
                # print(new_goals, substitution)

                KB.add_goals(new_goals, substitution)

    def _check_goals(self):
        # debug_display('CG_KB_G', KB.goals, self.current_time)
        solutions = SOLVER.solve_goals(self.current_time)

        debug_display('SOLUTIONS_ENGINE', solutions)
        # debug_display('SOLUTION_COUNT', self.current_time, len(solutions))

        process_solutions(solutions, self.current_time)

        # debug_display('KB_FLUENTS_ENGINE', self.current_time, KB.fluents)


ENGINE = _ENGINE()
