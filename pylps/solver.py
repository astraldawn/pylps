'''
Revised solver that will recursively yield solutions
'''
import copy

from collections import deque

from functools import partial
from unification import *

from pylps.constants import *
from pylps.expand import *
from pylps.exceptions import *
from pylps.utils import *
from pylps.kb import KB
from pylps.config import CONFIG

from pylps.state import State, Proposed, Solution

from pylps.unifier import unify_fact, unify_fluent, unify_action
from pylps.constraints import constraints_satisfied

import pylps.solver_utils as s_utils


class _Solver(object):

    def __init__(self):
        self.current_time = 1
        self.cycle_proposed = Proposed()
        self.iterations = 0

        # Reactive rule solving
        self.reactive = False
        self.only_facts = False

    def solve_goals(self, current_time):
        '''
        Entry point, attempt to solve reactive rules
        Note that reactive rules R1 .. RN are not ANDs
        This prevents the reuse of the solver for each indivdual reactive
        rule
        '''

        self.current_time = current_time
        self.cycle_proposed = Proposed()
        self.iterations = 0

        strategy = CONFIG.strategy

        solvers = {
            STRATEGY_DEFAULT: self.main_solver,
            STRATEGY_COMB: self.alternate_solver,
            STRATEGY_GREEDY: self.greedy_solver,
            STRATEGY_GREEDY_FAST: partial(self.greedy_solver, fast_solve=True)
        }

        solutions = solvers[strategy]()

        return solutions

    def main_solver(self):
        proposed_stack = []
        states_stack = []
        reactive_soln = {}

        cur_goal_pos = 0
        end = False
        back = False

        max_soln = 0
        soln_cnt = 0
        solutions = []

        solver_loop_iterations = 0
        solver_loop_iterations_limit = 500  # VERY IMPORTANT FOR PERFORMANCE

        n_solutions = CONFIG.n_solutions

        while not end:

            # FORWARD
            while not back:
                solver_loop_iterations += 1
                if solver_loop_iterations > solver_loop_iterations_limit:
                    end = True
                    break

                if cur_goal_pos >= len(KB.goals):

                    if len(self.cycle_proposed.actions) >= max_soln:
                        solutions.append(Solution(
                            proposed=copy.deepcopy(self.cycle_proposed),
                            states=copy.deepcopy(states_stack)
                        ))
                        max_soln = len(self.cycle_proposed.actions)

                    soln_cnt += 1
                    if soln_cnt >= n_solutions:
                        end = True
                        break

                    back = True
                    continue

                # debug_display('FORWARD', cur_goal_pos)

                multigoal = KB.goals[cur_goal_pos]

                reactive_soln[cur_goal_pos] = self.backtrack_solve(multigoal)

                new_state = next(reactive_soln[cur_goal_pos])

                self.add_cycle_proposed(new_state)
                proposed_stack.append(copy.deepcopy(self.cycle_proposed))
                states_stack.append(copy.deepcopy(new_state))

                cur_goal_pos += 1

            if end:
                break

            # BACK
            while back:
                solver_loop_iterations += 1
                if solver_loop_iterations > solver_loop_iterations_limit:
                    end = True
                    break

                cur_goal_pos -= 1
                # debug_display('BACK', cur_goal_pos)

                # No more options, even for the first goal
                if cur_goal_pos < 0:
                    end = True
                    break

                # GO BACK TO PREV STATE
                if proposed_stack:

                    proposed_stack.pop()
                    states_stack.pop()

                    try:
                        self.cycle_proposed = copy.deepcopy(proposed_stack[-1])
                    except IndexError:
                        self.cycle_proposed = Proposed()
                else:
                    self.cycle_proposed = Proposed()

                try:
                    # Do we have another solution?
                    new_state = next(reactive_soln[cur_goal_pos])
                    back = False
                    self.add_cycle_proposed(new_state)
                    proposed_stack.append(copy.deepcopy(self.cycle_proposed))
                    states_stack.append(copy.deepcopy(new_state))
                    cur_goal_pos += 1
                except StopIteration:
                    continue

        solutions = sorted(
            solutions,
            # Go for maximum solved + maximum number of actions
            key=lambda sol: (sol.solved, len(sol.proposed.actions)),
            reverse=True)

        return solutions

    def alternate_solver(self):
        solutions = []
        backtrack_solutions = {}
        empty_state = State([], {})
        goal_ids = []

        if len(KB.goals) == 0:
            solutions.append(Solution(
                proposed=[], states=[])
            )

        for i, goal in enumerate(KB.goals):
            backtrack_solutions[i] = list(self.backtrack_solve(goal))

            goal_ids.append([
                NON_S if s == empty_state else c
                for c, s in enumerate(backtrack_solutions[i])
            ])

        # debug_display('ALT_SOLVER', backtrack_solutions)

        for comb in generate_combinations(goal_ids):
            self.cycle_proposed.reset()
            for p, s in enumerate(comb):
                self.add_cycle_proposed(backtrack_solutions[p][s])

            actions_valid = True
            for p, s in enumerate(comb):
                if not actions_valid:
                    continue

                cur_state = backtrack_solutions[p][s]
                for action in cur_state.actions:
                    if not actions_valid:
                        continue

                    res = constraints_satisfied(
                        action, cur_state, Proposed())

                    if not res:
                        actions_valid = False

            if actions_valid:
                solutions.append(Solution(
                    proposed=copy.deepcopy(self.cycle_proposed),
                    states=[
                        backtrack_solutions[p][s] for p, s in enumerate(comb)
                    ]
                ))

        return solutions

    def greedy_solver(self, fast_solve=False):

        solutions = []
        fast_solve = fast_solve

        if len(KB.goals) == 0:
            solutions.append(Solution(
                proposed=Proposed(), states=[])
            )
            return solutions

        valid_results = set([G_SOLVED, G_DEFER])
        solutions = [
            Solution(proposed=Proposed(), states=[])
        ]

        for i, goal in enumerate(KB.goals):

            backtrack_solve = self.backtrack_solve(goal)

            seen_actions = {
                sol_id: set() for sol_id, _ in enumerate(solutions)}
            goal_states = {sol_id: [] for sol_id, _ in enumerate(solutions)}
            goal_solved = False

            while True and not goal_solved:
                try:
                    cur_state = next(backtrack_solve)
                except StopIteration:
                    break

                if cur_state.result is G_DISCARD:
                    break

                s_utils.reify_actions(cur_state, reify=True)

                for sol_id, solution in enumerate(solutions):
                    actions_valid = True
                    for action in cur_state.actions:
                        if not actions_valid:
                            continue

                        res = constraints_satisfied(
                            action, cur_state, solution._proposed)

                        if not res:
                            actions_valid = False

                    if not actions_valid:
                        # debug_display('INVALID_STATE',
                        #               self.current_time, cur_state)
                        continue

                    if cur_state.result in valid_results:
                        debug_display(
                            'VALID_STATE', self.current_time, cur_state)
                        prev_seen_len = len(seen_actions[sol_id])

                        if CONFIG.experimental:
                            for action in cur_state.actions:
                                if action.BaseClass is ACTION:
                                    seen_actions[sol_id].add(action)
                        else:
                            for action in cur_state.actions:
                                seen_actions[sol_id].add(action)

                        if prev_seen_len != len(seen_actions[sol_id]) \
                                or cur_state.result is G_SOLVED \
                                or cur_state.reactive_only:
                            goal_states[sol_id].append(
                                cur_state)

                        # Only want the first solution for a goal
                        if cur_state.result is G_SOLVED and fast_solve:
                            goal_solved = True
                            break

            new_solutions = []
            for sol_id, g_states in goal_states.items():
                if g_states == []:
                    new_solutions.append(solutions[sol_id])

                for i, g_state in enumerate(g_states):
                    if i == len(g_states) - 1:
                        t_soln = solutions[sol_id]
                    else:
                        t_soln = copy.deepcopy(solutions[sol_id])

                    s_utils.add_to_cycle_proposed(
                        t_soln._proposed, g_state)
                    t_soln.add_state(g_state)

                    new_solutions.append(t_soln)

            solutions = new_solutions

        solutions = sorted(
            solutions,
            key=lambda x: (x.solved, ), reverse=True
        )

        return solutions

    def add_cycle_proposed(self, state):
        # Add current state
        self.cycle_proposed.add_actions(
            s_utils.reify_actions(state, reify=True))

    def display_cycle_proposed(self):
        for action in self.cycle_proposed.actions:
            display(action)
        display()

    def backtrack_solve(
        self, start: State, pos=0,
        reactive=False, only_facts=False,  # Reactive rule solver
        current_time=None
    ):
        '''
        AND step of solving
        Solve all inside here, except for the case when deferring
        This function should return a generator
        '''
        self.reactive = reactive
        self.only_facts = only_facts
        self.states = deque()

        '''
        Additional empty state to cover the case where
        the reactive rule is not chosen for solving
        '''
        if CONFIG.solution_preference is SOLN_PREF_MAX and \
                CONFIG.strategy is STRATEGY_DEFAULT:
            yield State([], {})

        start_state = copy.deepcopy(start)
        self.states.append(start_state)

        if current_time:
            self.current_time = current_time

        while self.states:
            # cur_state = states.popleft()
            cur_state = self.states.pop()

            self.iterations += 1

            # debug_display('STATE_BT', cur_state)

            if cur_state.result is G_DEFER or cur_state.result is G_DISCARD:
                yield cur_state
                continue

            # Nothing left
            goal = cur_state.get_next_goal(reactive=reactive)

            if self.iterations > 10000 and CONFIG.debug:
                break

            # debug_display(self.iterations, goal)
            # debug_display('STATE_BT', cur_state)

            if not goal:
                cur_state.set_result(G_SOLVED)
                yield cur_state
            else:
                self.expand_goal(goal, cur_state)

        if CONFIG.solution_preference is SOLN_PREF_FIRST:
            yield State([], {})

    def expand_goal(self, goal, cur_state):

        outcome = True
        states = self.states
        cur_state.compress(cpos=1)

        if isinstance(goal, tuple):
            outcome, goal = goal[1], goal[0]

        # debug_display('EXPAND', self.current_time, goal, outcome)
        # debug_display('EXPAND_R', reify_obj_args(goal, cur_state.subs))

        # if self.reactive and \
        #         (goal.BaseClass is ACTION):
        #     self.expand_action_reactive(goal, cur_state, states)
        #     return

        if goal.BaseClass is ACTION:
            self.expand_action(goal, cur_state, states, outcome)
        elif goal.BaseClass is EVENT:
            if goal.completed and CONFIG.experimental:
                self.expand_action(goal, cur_state, states, outcome,
                                   completed_event=True)
                return
            self.expand_event(goal, cur_state, states, outcome)
        elif goal.BaseClass is EXPR:
            expand_expr(goal, cur_state, states)
        elif goal.BaseClass is FACT:
            self.expand_fact(goal, cur_state, states)
        elif goal.BaseClass is FLUENT:
            self.expand_fluent(goal, cur_state, states, outcome)
        else:
            raise UnimplementedOutcomeError(goal.BaseClass)

        # debug_display()

    def expand_action(self, goal, cur_state, states, outcome=None,
                      completed_event=False):
        new_state = cur_state  # REMOVED_DEEPCOPY
        cur_subs = cur_state.subs

        if self.reactive or goal.from_reactive and not completed_event:
            from_kb = list(unify_action(goal, self.current_time))

            for i, sub in enumerate(from_kb):
                if i == len(from_kb) - 1:
                    new_state = cur_state
                else:
                    new_state = copy.deepcopy(cur_state)

                new_state.update_subs(sub)
                states.append(new_state)

            if from_kb:
                return

            new_state._goal_pos -= 1
            mod_g = new_state._goals[new_state.goal_pos]

            if isinstance(mod_g, tuple):
                mod_g[0].from_reactive = True
            else:
                mod_g.from_reactive = True

            new_state.set_result(G_DEFER)
            states.append(new_state)
            return

        # Handle temporal variables (atomic action)
        start_time = var(goal.start_time.name)
        end_time = var(goal.end_time.name)

        # debug_display('ACTION', goal, start_time, end_time)
        # debug_display('ACTION_SUBS', cur_subs)

        r_start_time = reify(start_time, cur_subs)

        # if completed_event:
        #     debug_display('COMPLETED_EVENT', goal)
        #     r_start_time = reify(start_time, cur_subs)
        #     r_end_time = reify(end_time, cur_subs)

        #     debug_display('S / E', start_time, end_time,
        #                   self.current_time, r_start_time, r_end_time)
        #     debug_display('CUR_SUBS', cur_subs)

        '''
        TODO

        NEED TO FIX FOR RIVER CROSSING
        '''
        # if not cur_subs.get(start_time)  \
        #         or not isinstance(cur_subs[start_time], int):
        if not isinstance(r_start_time, int):
            # If it is a completed event and we don't have subs, it is fine
            if completed_event:
                pass

            # Start time has not been substituted
            elif cur_state.temporal_used:
                new_state._goal_pos -= 1

                new_state.set_result(G_DEFER)
                states.append(new_state)
                return
            else:
                unify_start = unify(start_time, self.current_time)
                unify_end = unify(end_time, self.current_time + 1)
                new_state.update_subs(unify_start)
                new_state.update_subs(unify_end)
                new_state.temporal_used_true()
        else:
            # debug_display('START HAS ALREADY BEEN UNIFIED')
            # debug_display(cur_state)
            if not isinstance(cur_subs[start_time], int):
                new_state.temporal_used_true()
                # pass

            unify_start = unify(start_time, r_start_time)
            new_state.update_subs(unify_start)

            r_end_time = r_start_time + 1
            if completed_event:
                r_end_time = reify(end_time, cur_subs)

            unify_end = unify(end_time, r_end_time)
            new_state.update_subs(unify_end)

            if completed_event and CONFIG.experimental:
                if not isinstance(r_end_time, int):
                    new_state._subs[end_time] = r_start_time

            temporal_valid = new_state.subs[end_time] <= self.current_time + 1
            temporal_exceed = new_state.subs[end_time] - self.current_time < 1

            if not temporal_valid:
                new_state._goal_pos -= 1

                new_state.set_result(G_DEFER)
                # debug_display('DEFER_ELSE', goal)
                states.append(new_state)
                return

            # Only apply temporal exceed for actions
            if temporal_exceed and not completed_event:
                new_state.set_result(G_DISCARD)
                states.append(new_state)
                return

        # If we execute the action, is it valid here?
        valid = None
        if CONFIG.strategy is STRATEGY_DEFAULT:
            valid = constraints_satisfied(
                goal, new_state, self.cycle_proposed)

        # if not valid and CONFIG.debug:
        #     debug_display('C_CHECK_F', goal)
        #     print()
        #     debug_display('C_CHECK_F_STATE', new_state)
        #     print()
        #     debug_display('C_CHECK_F_PROPOSED', self.cycle_proposed)
        #     print('\n\n')

        # Done
        if valid or CONFIG.strategy is not STRATEGY_DEFAULT:
            new_state.add_action(goal)  # REMOVED_DEEPCOPY
            states.append(new_state)

    def expand_action_reactive(self, goal, cur_state, states):
        debug_display('EXPAND_A_R', goal)

        for sub in list(unify_action(goal, self.current_time)):
            new_state = copy.deepcopy(cur_state)
            new_state.update_subs(sub)
            states.append(new_state)

    def expand_event(self, goal, cur_state, states, outcome=True):
        # debug_display('EXPAND_EVENT', goal)

        if self.reactive:
            from_kb = list(unify_action(goal, self.current_time))

            for i, sub in enumerate(from_kb):
                if i == len(from_kb) - 1:
                    new_state = cur_state
                else:
                    new_state = copy.deepcopy(cur_state)

                new_state.update_subs(sub)
                states.append(new_state)

            if from_kb:
                return

        all_false = True
        all_true = True
        res_success = 0

        # Need to reverse here for DFS like iteration
        KB_clauses = list(KB.get_clauses(goal))

        KB_clauses.reverse()

        if KB_clauses:
            if CONFIG.single_clause:
                KB_clauses = [KB_clauses[-1]]

            for i, clause in enumerate(KB_clauses):
                is_single = (i == len(KB_clauses) - 1)
                res = self.match_event(
                    goal, clause, cur_state, states, outcome,
                    is_single=is_single)

                # debug_display('ME', goal, clause, res)

                if res:
                    res_success += 1
                    all_false = False
                else:
                    all_true = False
        else:
            # cannot be false if no clauses
            all_false = False

        # Negation of goals
        if not outcome:
            if all_false:
                new_state = cur_state  # REMOVED_DEEPCOPY
                states.append(new_state)

            if all_true:
                # The successful states must be popped off the stack
                for i in range(res_success):
                    states.pop()

                new_state = cur_state  # REMOVED_DEEPCOPY
                new_state.set_result(G_DISCARD)
                states.append(new_state)

    def match_event(self, goal, clause, cur_state, states, outcome,
                    is_single):
        cur_subs = cur_state.subs

        # Reify if possible
        # goal.args = reify_args(goal.args, cur_subs)
        goal_args = reify_args(goal.args, cur_subs)

        # debug_display('ME_REIFY_ARGS', goal_args)
        # debug_display('ME_REIFY_SUBS', cur_subs)

        new_reqs = []
        new_subs = {}
        counter = cur_state.counter + 1

        for clause_arg, goal_arg in zip(clause.goal[0].args, goal_args):
            match_res = s_utils.match_clause_goal(
                clause_arg, goal_arg,
                new_subs, counter
            )

            # debug_display('MATCH_RES', clause_arg, goal_arg, match_res)
            # debug_display()

            # If the matching fails, cannot proceed, return
            if not match_res:
                return False

        if is_single:
            new_state = cur_state
        else:
            new_state = copy.deepcopy(cur_state)

        new_state.reactive_only = goal.from_reactive
        new_state._counter += 1

        s_utils.create_clause_variables(
            clause, counter, goal, cur_subs, new_subs, new_reqs,
            reactive=goal.from_reactive
        )

        new_state.update_subs(new_subs)

        for n_req in new_reqs:
            # Check if it is possible to continue, otherwise hold off
            req = n_req
            if isinstance(n_req, tuple):
                req = n_req[0]
            if req.BaseClass is ACTION:
                start_time = reify(var(req.start_time.name), new_state.subs)
                end_time = reify(var(req.end_time.name), new_state.subs)

                if (isinstance(start_time, Var) or isinstance(end_time, Var)) \
                        and new_state.temporal_used:
                    new_state.set_result(G_DEFER)

        new_state.replace_event(goal, outcome, new_reqs)  # REMOVED_DEEPCOPY
        states.append(new_state)

        return True

    def expand_fact(self, fact, cur_state, states):
        cur_subs = cur_state.subs
        r_fact = reify_obj_args(fact, cur_subs)
        grounded = is_grounded(r_fact)

        # debug_display('FACT', fact, grounded)

        # Only facts checks if the reactive rule is only made up of facts
        # In that case, trigger once
        if self.only_facts:
            all_subs = list(unify_fact(fact, reactive=self.only_facts))
        else:
            all_subs = list(unify_fact(r_fact))

        # debug_display('EXPAND_F', all_subs)

        # Handle the case where fact is grounded (existence check)
        if grounded:
            if all_subs[0]:
                new_state = cur_state  # REMOVED_DEEPCOPY
                states.append(new_state)

            return

        subs = []

        for sub in all_subs:
            valid_sub = True
            for k, v in sub.items():
                if not valid_sub:
                    continue

                # Do not want to consider local variables here
                if cur_subs.get(k) and VAR_SEPARATOR in k.token:
                    res = reify(k, cur_subs)
                    if not isinstance(res, Var) and v != res:
                        valid_sub = False

            if valid_sub:
                subs.append(sub)

        subs.reverse()

        # debug_display('EXPAND_FACT_VALID_SUBS', subs)

        for i, sub in enumerate(subs):
            if i == len(subs) - 1:
                new_state = cur_state
            else:
                new_state = copy.deepcopy(cur_state)

            new_state.update_subs(sub)
            states.append(new_state)

    def expand_fluent(self, fluent, cur_state, states, outcome=True):
        cur_subs = cur_state.subs
        f_time = reify(var(fluent.time.name), cur_subs)

        # debug_display('FLUENT', fluent, outcome, cur_subs)
        # debug_display('FTIME / CTIME', f_time, self.current_time)

        try:
            if not isinstance(f_time, int) and f_time.BaseClass is CONSTANT:
                f_time = f_time.const

            if f_time > self.current_time:
                new_state = cur_state  # REMOVED_DEEPCOPY
                new_state._goal_pos -= 1
                new_state.set_result(G_DEFER)
                states.append(new_state)
                return
        except AttributeError:
            pass

        # TODO: There might be a need for better temporal handling here
        all_subs = list(unify_fluent(
            fluent, self.current_time, counter=cur_state.counter))

        debug_display('FLUENT_ALL_SUBS', all_subs, cur_state.counter)

        subs = []

        for sub in all_subs:
            valid_sub = True
            for k, v in sub.items():
                if not valid_sub:
                    continue

                if cur_subs.get(k):
                    res = reify(k, cur_subs)
                    # debug_display('F_MATCH_SUBS', v, res)
                    v_c = v
                    r_c = res
                    if is_constant(v_c):
                        v_c = LPSConstant(v_c)

                    if is_constant(r_c):
                        r_c = LPSConstant(r_c)

                    if not isinstance(res, Var) and v_c != r_c:
                        valid_sub = False

            if valid_sub:
                subs.append(sub)

        subs.reverse()

        # debug_display('FLUENT_ALL_SUBS_FILTER', subs)
        # debug_display('KB_FLUENTS', KB.fluents)

        if outcome:
            # if not subs:
            #     debug_display('FLUENT_CHECK_F_DEFER')
            #     new_state = copy.deepcopy(cur_state)
            #     new_state._goal_pos -= 1
            #     new_state.set_result(G_DEFER)
            #     states.append(new_state)
            #     return

            for i, sub in enumerate(subs):
                if i == len(subs) - 1:
                    new_state = cur_state
                else:
                    new_state = copy.deepcopy(cur_state)

                new_state.update_subs(sub)
                states.append(new_state)

        elif not outcome:
            # TODO: Is it possible to have a sub but not match it? Or is
            # it such that no sub can be matched?
            # new_state = copy.deepcopy(cur_state)
            new_state = cur_state  # REMOVED_DEEPCOPY
            if subs:
                # debug_display('FLUENT_CHECK_F_DEFER')
                new_state._goal_pos -= 1
                new_state.set_result(G_DEFER)
                states.append(new_state)
                return

            if not subs:
                states.append(new_state)


SOLVER = _Solver()
