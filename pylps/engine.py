import copy

from ordered_set import OrderedSet
from pylps.utils import *

from pylps.kb import KB
from pylps.causality import unify_obs, commit_outcomes
from pylps.unifier import reify_goals
from pylps.solver import SOLVER
from pylps.solver_utils import process_solutions
from pylps.plan import Plan


class _ENGINE(object):
    start_time = 0
    current_time = 0
    max_time = 5

    def set_params(self, max_time):
        self.max_time = max_time
        KB.max_time = max_time

    def run(self, stepwise=False):
        self.current_time = self.start_time

        if not stepwise:
            while self.current_time <= self.max_time:
                if self.current_time == 0:
                    self._handle_initial()
                else:
                    self._next_iteration()

                self.current_time += 1

    def next_step(self):
        if self.current_time > self.max_time:
            return

        if self.current_time == 0:
            self._handle_initial()
        else:
            self._next_iteration()

        self.current_time += 1

    def _next_iteration(self):

        self.initiated = OrderedSet()
        self.terminated = OrderedSet()

        obs_strategy = {
            OBS_AFTER: self._obs_after,
            OBS_BEFORE: self._obs_before
        }

        obs_strategy[CONFIG.obs]()

    def _obs_after(self):
        KB.clear_cycle_obs(self.current_time)

        self._check_rules()
        self._solve_plans()
        self._check_observations()

        commit_outcomes(self.initiated, self.terminated)

    def _obs_before(self):
        KB.clear_cycle_obs(self.current_time)

        self._check_observations()
        self._check_rules()
        self._solve_plans()

        commit_outcomes(self.initiated, self.terminated)

    def _check_observations(self):

        for observation in KB.observations:
            if observation.end_time - 1 == self.current_time:
                ret = unify_obs(observation)
                if ret:
                    i, t = ret
                    self.initiated |= i
                    self.terminated |= t

    def _handle_initial(self):
        for fluent in KB.initial_fluents:
            KB.add_fluent(fluent)
            KB.log_fluent(fluent, 0, F_INITIATE)

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

                cond_object.from_reactive = True

                rename_args(0, cond_object)
                conds.append(cond_object)

            # Special case for rules beginning with True
            if len(conds) == 1 and conds[0].BaseClass is CONSTANT and \
                    conds[0].const is True:
                true_trigger = True
                rule._constant_trigger = True
                state_list = [Plan([], {}, result=G_SOLVED)]

            # fact only
            if only_facts:
                rule._constant_trigger = True

            if not true_trigger:

                state_list = list(SOLVER.backtrack_solve(
                    start=Plan(conds, {}),  # REMOVED_DEEPCOPY
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
                    KB.add_plan(new_goals, subs)

                if result is G_DEFER:
                    defer = list(state.goals)[state.goal_pos:]
                    new_goals = defer + new_goals
                    KB.add_plan(new_goals, subs)

    def _solve_plans(self):
        # debug_display('CG_B_TIME / N_GOALS', self.current_time, len(KB.plans))
        # debug_display('CG_KB_BEF', KB.plans)
        solutions = SOLVER.solve_goals(self.current_time)

        # print(self.current_time, solutions)

        # debug_display('CG_S_TIME / N_SOLN', self.current_time, len(solutions))
        # debug_display('CG_SOLN', solutions)

        process_solutions(solutions, self.current_time)

        # debug_display('KB_FLUENTS_ENGINE', self.current_time, KB.fluents)


ENGINE = _ENGINE()
