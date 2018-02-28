'''
Revised solver that will recursively yield solutions
'''
import copy
from unification import *
from collections import deque

from pylps.constants import *
from pylps.exceptions import *
from pylps.utils import *
from pylps.kb import KB
from pylps.config import CONFIG

from pylps.lists import LPSList
from pylps.state import State, Proposed

from pylps.unifier import unify_fact
from pylps.constraints import constraints_satisfied


class _Solver(object):

    def __init__(self):
        self.current_time = None
        self.cycle_proposed = Proposed()
        self.iterations = 0

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

        proposed_stack = []
        states_stack = []
        reactive_soln = {}

        cur_goal_pos = 0
        end = False
        back = False

        max_soln = 0
        soln_cnt = 0
        solutions = []
        n_solutions = CONFIG.n_solutions

        while not end:

            # FORWARD
            while not back:
                if cur_goal_pos >= len(KB.goals):

                    if len(self.cycle_proposed.actions) >= max_soln:
                        solutions.append((
                            copy.deepcopy(self.cycle_proposed),
                            copy.deepcopy(states_stack)
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

        return solutions

    def add_cycle_proposed(self, state):
        for action in state.actions:
            action.args = reify_args(action.args, state.subs)
            action.update_start_time(
                reify_args([action.start_time], state.subs)[0])
            action.update_end_time(
                reify_args([action.end_time], state.subs)[0])

            self.cycle_proposed.add_action(action)

        if not CONFIG.cycle_fluents:
            return

        for fluent_outcome in state.fluents:
            # May not need this actually
            fluent = fluent_outcome.fluent
            fluent.args = reify_args(fluent.args, state.subs)

            self.cycle_proposed.add_fluent(fluent_outcome)

    def display_cycle_proposed(self):
        for action in self.cycle_proposed.actions:
            display(action)
        display()

    def backtrack_solve(self, start: State, pos=0):
        '''
        AND step of solving
        Solve all inside here, except for the case when deferring
        This function should return a generator
        '''
        states = deque()

        start_state = copy.deepcopy(start)
        states.append(start_state)

        while states:
            cur_state = states.pop()

            self.iterations += 1

            if cur_state.result is G_DEFER or cur_state.result is G_DISCARD:
                yield cur_state
                continue

            # Nothing left
            goal = cur_state.get_next_goal()

            # if self.iterations > 5:
            #     break

            # debug_display(self.iterations, goal)
            # debug_display(cur_state)

            if not goal:
                cur_state.set_result(G_SOLVED)
                yield cur_state
            else:
                self.expand_goal(goal, cur_state, states)

        '''
        Additional empty state to cover the case where
        the reactive rule is not chosen for solving
        '''
        yield State([], {})

    def expand_goal(self, goal, cur_state, states):

        if goal.BaseClass is ACTION:
            self.expand_action(goal, cur_state, states)
        elif goal.BaseClass is EVENT:
            self.expand_event(goal, cur_state, states)
        elif goal.BaseClass is FACT:
            self.expand_fact(goal, cur_state, states)
        else:
            raise UnimplementedOutcomeError(goal.BaseClass)

    def expand_action(self, goal, cur_state, states):
        new_state = copy.deepcopy(cur_state)

        # new_state.remove_first_goal()

        # Handle temporal variables (atomic action)
        start_time = var(goal.start_time.name)
        end_time = var(goal.end_time.name)

        if start_time not in cur_state.subs:
            # Start time has not been substituted
            if cur_state.temporal_used:
                print('TEMPORAL VAR USED')
            else:
                unify_start = unify(start_time, self.current_time)
                unify_end = unify(end_time, self.current_time + 1)
                new_state.update_subs(unify_start)
                new_state.update_subs(unify_end)
                new_state.temporal_used_true()
        else:
            # debug_display('START HAS ALREADY BEEN UNIFIED')
            # debug_display(cur_state)

            unify_end = unify(end_time, cur_state.subs[start_time] + 1)
            new_state.update_subs(unify_end)
            temporal_valid = new_state.subs[end_time] <= self.current_time + 1

            if not temporal_valid:
                new_state._goal_pos -= 1
                new_state.set_result(G_DEFER)
                states.append(new_state)
                return

            temporal_exceed = new_state.subs[end_time] - self.current_time < 1

            if temporal_exceed:
                new_state.set_result(G_DISCARD)
                states.append(new_state)
                return

        # If we execute the action, is it valid here?
        valid = constraints_satisfied(
            goal, new_state, self.cycle_proposed)

        # debug_display(goal, new_state.subs, valid)
        # debug_display()

        # Done
        if valid:
            new_state.add_action(copy.deepcopy(goal))

            if CONFIG.cycle_fluents:
                causalities = KB.exists_causality(goal)

                if causalities:
                    for outcome in causalities.outcomes:
                        new_state.add_fluent(copy.deepcopy(outcome))

            states.append(new_state)

    def expand_event(self, goal, cur_state, states):

        # Need to reverse here for DFS like iteration
        KB_clauses = list(KB.get_clauses(goal))
        KB_clauses.reverse()

        if KB_clauses:
            if CONFIG.single_clause:
                KB_clauses = [KB_clauses[-1]]

            for clause in KB_clauses:
                '''
                TODO: Actually resolving the temporal requirements correctly
                Simple replacement for now
                '''

                '''Experimental list handling'''
                self.match_event(goal, clause, cur_state, states)
                # if goal.args[0].BaseClass is LIST:
                #     if isinstance(clause.goal[0].args[0], tuple):
                #         debug_display('LIST', clause)
                #         continue

                #     if clause.goal[0].args[0].BaseClass is VARIABLE:
                #         if len(goal.args[0]) != 1:
                #             continue

                # new_state = copy.deepcopy(cur_state)
                # new_state.replace_event(goal, clause.reqs)
                # states.append(new_state)

    def match_event(self, goal, clause, cur_state, states):
        # has_args = len(goal.args) > 0
        cur_subs = cur_state.subs

        # Reify?
        # debug_display(goal, clause, cur_state.subs)

        new_state = copy.deepcopy(cur_state)
        new_state._counter += 1
        new_reqs = []
        new_subs = {}
        counter = new_state.counter

        for clause_arg, goal_arg in zip(clause.goal[0].args, goal.args):
            new_subs.update({
                var(clause_arg.name + '_' + str(counter)): var(goal_arg.name)
            })

        for req in clause.reqs:
            new_req = copy.deepcopy(req)

            for arg in new_req.args:
                if isinstance(arg, int):
                    continue

                if arg.BaseClass is VARIABLE:
                    arg.name += '_' + str(counter)

            new_reqs.append(new_req)

        new_state.update_subs(new_subs)

        # if has_args and goal.args[0].BaseClass is LIST:
        #     if isinstance(clause.goal[0].args[0], tuple):
        #         clause_goal_arg = clause.goal[0].args[0]

        #         # debug_display(clause_goal_arg, goal.args[0])

        #         if clause_goal_arg[0] is MATCH_LIST_HEAD:
        #             subs = {
        #                 var(clause_goal_arg[1].name): goal.args[0].head,
        #                 var(clause_goal_arg[2].name):
        #                     LPSList(goal.args[0].rest)
        #             }
        #             new_state = copy.deepcopy(cur_state)
        #             new_state.update_subs(subs)
        #             new_state.replace_event(goal, clause.reqs)
        #             states.append(new_state)
        #         return

        #     if clause.goal[0].args[0].BaseClass is VARIABLE:
        #         if len(goal.args[0]) != 1:
        #             return

        new_state.replace_event(goal, copy.deepcopy(new_reqs))
        states.append(new_state)

    def expand_fact(self, fact, cur_state, states):
        cur_subs = cur_state.subs
        all_subs = list(unify_fact(fact))
        subs = []

        for sub in all_subs:
            valid_sub = True
            for k, v in sub.items():
                if not valid_sub:
                    continue

                if cur_subs.get(k):
                    res = reify(k, cur_subs)
                    if v != res and not isinstance(res, Var):
                        valid_sub = False

            if valid_sub:
                subs.append(sub)

        subs.reverse()

        for sub in subs:
            new_state = copy.deepcopy(cur_state)
            new_state.update_subs(sub)
            states.append(new_state)


SOLVER = _Solver()
