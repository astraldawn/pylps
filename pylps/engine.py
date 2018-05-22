import copy

from pylps.utils import *

from pylps.kb import KB
from pylps.causality import unify_obs
from pylps.unifier import reify_goals
from pylps.solver import SOLVER
from pylps.solver_utils import process_solutions
from pylps.state import State


class _ENGINE(object):
    start_time = 1
    current_time = 1
    max_time = 5

    def set_params(self, max_time):
        self.max_time = max_time

    def run(self, stepwise=False):
        self.current_time = self.start_time
        KB.reset_goals()

        if not stepwise:
            while self.current_time <= self.max_time:
                self._next_iteration()

    def next_step(self):
        if self.current_time > self.max_time:
            return

        self._next_iteration()

    def _next_iteration(self):
        self._check_rules()
        self._check_goals()
        self._check_observations()

        self.current_time += 1

        KB.clear_cycle_obs(current_time=self.current_time)

    def _check_observations(self):
        for observation in KB.observations:
            if observation.start_time == self.current_time:
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
            only_facts = True

            for cond in rule.conds:
                cond_object = copy.deepcopy(cond)

                # Flag setting for fact triggers
                if cond_object.BaseClass != FACT:
                    only_facts = False

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
                    only_facts=only_facts,
                    current_time=self.current_time
                ))

                substitutions = [s.subs for s in subs_list]

            # debug_display(
            #     'ENGINE_C_R_',
            #     true_trigger, conds, substitutions, self.current_time)

            if not substitutions:
                continue

            for substitution in substitutions:
                if substitution == {} and not true_trigger:
                    continue

                new_goals = reify_goals(rule.goals, substitution)
                # debug_display('SUB_NEW_GOALS', new_goals, substitution)

                KB.add_goals(new_goals, substitution)

    def _check_goals(self):
        debug_display('CG_B_TIME / N_GOALS', self.current_time, len(KB.goals))
        debug_display('CG_KB_BEF', KB.goals)
        solutions = SOLVER.solve_goals(self.current_time)

        debug_display('CG_S_TIME / N_SOLN', self.current_time, len(solutions))
        debug_display('CG_SOLN', solutions)

        process_solutions(solutions, self.current_time)

        # debug_display('CG_A_TIME / N_GOALS', self.current_time, len(KB.goals))
        # debug_display('CG_KB_AFT', KB.goals)

        # debug_display('KB_FLUENTS_ENGINE', self.current_time, KB.fluents)


ENGINE = _ENGINE()
