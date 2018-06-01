import copy

from ordered_set import OrderedSet
from pylps.utils import *

from pylps.kb import KB
from pylps.causality import unify_obs, commit_outcomes
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
        KB.max_time = max_time

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

        self.initiated = OrderedSet()
        self.terminated = OrderedSet()

        self._check_observations()
        self._check_rules()

        # Flag cycle observations for removal, remove prev cycle actions
        KB.clear_cycle_obs(self.current_time)

        debug_display('CYCLE_OBS', self.current_time, KB.cycle_obs)

        self._check_goals()

        commit_outcomes(self.initiated, self.terminated)

        # Flag prev cycle actions for removal, remove cycle observations
        KB.clear_cycle_obs(self.current_time)

        self.current_time += 1

    def _check_observations(self):

        for observation in KB.observations:
            if observation.start_time == self.current_time:
                ret = unify_obs(observation)
                if ret:
                    i, t = ret
                    self.initiated |= i
                    self.terminated |= t

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

                # TODO: What if its hidden inside an EXPR?

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
                state_list = [State([], {}, result=G_SOLVED)]

            # fact only
            if only_facts:
                rule._constant_trigger = True

            if not true_trigger:

                state_list = list(SOLVER.backtrack_solve(
                    start=State(copy.deepcopy(conds), {}),
                    reactive=True,
                    only_facts=only_facts,
                    current_time=self.current_time
                ))

                # debug_display('STATE_LIST', self.current_time, state_list)

            if not state_list:
                continue

            for state in state_list:
                subs = state.subs
                result = state.result
                # TODO: Not exactly, there may just be facts with constant
                if subs == {} and not (true_trigger or result is G_DEFER):
                    continue

                new_goals = reify_goals(rule.goals, subs)

                if result is G_SOLVED:
                    KB.add_goals(new_goals, subs)

                if result is G_DEFER:
                    defer = list(state.goals)[state.goal_pos:]
                    new_goals = defer + new_goals
                    KB.add_goals(new_goals, subs)

    def _check_goals(self):
        debug_display('CG_B_TIME / N_GOALS', self.current_time, len(KB.goals))
        debug_display('CG_KB_BEF', KB.goals)
        solutions = SOLVER.solve_goals(self.current_time)

        debug_display('CG_S_TIME / N_SOLN', self.current_time, len(solutions))
        debug_display('CG_SOLN', solutions)

        process_solutions(solutions, self.current_time)

        # debug_display('KB_FLUENTS_ENGINE', self.current_time, KB.fluents)


ENGINE = _ENGINE()
