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

from pylps.state import State

from pylps.unifier import unify_fact
# from pylps.solver import solve_multigoal
from pylps.constraints import constraints_satisfied_new


class _Solver(object):

    def __init__(self):
        self.current_time = None
        self.cycle_actions = []

    def solve_goals(self, current_time, n_solutions=1):
        '''
        Entry point, attempt to solve reactive rules
        Note that reactive rules R1 .. RN are not ANDs
        This prevents the reuse of the solver for each indivdual reactive
        rule
        '''
        self.current_time = current_time
        self.cycle_actions = []

        actions_stack = []
        states_stack = []
        reactive_soln = {}

        cur_goal_pos = 0
        end = False
        back = False

        max_soln = 0
        soln_cnt = 0
        solutions = []

        while not end:

            # FORWARD
            while not back:
                if cur_goal_pos >= len(KB.goals):

                    if len(self.cycle_actions) >= max_soln:
                        # self.display_cycle_actions()
                        solutions.append((
                            copy.deepcopy(self.cycle_actions),
                            copy.deepcopy(states_stack)
                        ))
                        max_soln = len(self.cycle_actions)

                    soln_cnt += 1
                    if soln_cnt >= n_solutions:
                        end = True
                        break

                    back = True
                    continue

                # print('FORWARD', cur_goal_pos)

                multigoal = KB.goals[cur_goal_pos]

                reactive_soln[cur_goal_pos] = self.backtrack_solve(multigoal)

                new_state = next(reactive_soln[cur_goal_pos])
                self.add_cycle_actions(new_state)
                actions_stack.append(copy.deepcopy(self.cycle_actions))
                states_stack.append(copy.deepcopy(new_state))

                cur_goal_pos += 1

                # self.display_cycle_actions()

            if end:
                break

            # BACK
            while back:
                cur_goal_pos -= 1
                # print('BACK', cur_goal_pos)

                # No more options, even for the first goal
                if cur_goal_pos < 0:
                    end = True
                    break

                # GO BACK TO PREV STATE
                if actions_stack:

                    actions_stack.pop()
                    states_stack.pop()

                    try:
                        self.cycle_actions = copy.deepcopy(actions_stack[-1])
                    except IndexError:
                        self.cycle_actions = []
                else:
                    self.cycle_actions = []

                try:
                    # Do we have another solution?
                    new_state = next(reactive_soln[cur_goal_pos])
                    back = False
                    self.add_cycle_actions(new_state)
                    actions_stack.append(copy.deepcopy(self.cycle_actions))
                    states_stack.append(copy.deepcopy(new_state))
                    cur_goal_pos += 1
                except StopIteration:
                    continue

                # print(actions_stack)

                # if actions_stack:
                #     actions_stack.pop()
                #     self.cycle_actions = actions_stack[-1]

                # for item in actions_stack:
                #     print(item)

            # end = True

            # DEBUG
            # return

            # if KB.goals not in states:
            #     states.add(copy.deepcopy(KB.goals))
            # else:
            #     # print(KB.goals)
            #     # print('DUPLICATE STATE')
            #     cur_goal_pos += 1
            #     continue

            # if multigoal.result in SOLVED_RESPONSES:
            #     solved_group.add(multigoal)
            #     backtracking_counter = 1

            # if multigoal.result is G_CLAUSE_FAIL:  # Go back one
            #     prev_pos = cur_goal_pos - backtracking_counter

            #     if prev_pos < 0:
            #         backtracking_counter = 1
            #         multigoal.update_result(G_DISCARD)
            #         cur_goal_pos += 1
            #         continue

            #     prev_goal = KB_goals[prev_pos]
            #     solved_group.remove(prev_goal)
            #     prev_goal.reset(propagate=True)
            #     backtracking_counter += 1
            #     continue
            # print(multigoal.result, cur_goal_pos)
            # print(goal_stk)

        return solutions

        # print(KB.goals)
        # max_solved = 0
        # for state in states:
        #     # print(self.current_time, state._to_tuple())
        #     solved = 0
        #     for child in state.children:
        #         if child.result in SOLVED_RESPONSES:
        #             solved += 1

        #     if solved > max_solved:
        #         KB.set_goals(state)
        #         max_solved = solved

        # if KB.goals:
        #     # KB.display_cycle_actions()
        #     new_children = []
        #     for child in KB.goals.children:
        #         if (child.result in SOLVED_RESPONSES or
        #                 child.result is G_DISCARD):
        #             continue
        #         # if(child.result in SOLVED_RESPONSES or
        #         #         child.result is G_DISCARD):
        #         #     continue
        #         elif child.result is G_FAIL_NO_SUBS:
        #             child.reset(propagate=True)
        #         new_children.append(child)

        #     KB.set_children(new_children)
        #     # print(KB.goals)
        #     process_cycle_actions()

    def add_cycle_actions(self, state):
        for action in state.actions:
            action.args = reify_args(action.args, state.subs)
            action.update_start_time(
                reify_args([action.start_time], state.subs)[0])
            action.update_end_time(
                reify_args([action.end_time], state.subs)[0])

            self.cycle_actions.append(action)

    def display_cycle_actions(self):
        for item in self.cycle_actions:
            print(item)
        print()

    def backtrack_solve(self, start: State, pos=0):
        '''
        AND step of solving
        Solve all inside here, except for the case when deferring
        This function should return a generator
        '''
        states = deque()

        # s_goals = deque([child.goal for child in start.children])
        # s_subs = start.subs
        start_state = copy.deepcopy(start)
        states.append(start_state)

        while states:
            cur_state = states.pop()

            # Nothing left
            goal = cur_state.get_next_goal()
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
            # Check if a sub is needed
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
            print('START HAS ALREADY BEEN UNIFIED')
            pass

        # If we execute the action, is it valid here?
        valid = constraints_satisfied_new(
            goal, new_state, self.cycle_actions)

        # print(goal, new_state.subs, valid)
        # print()

        # Done
        if valid:
            new_state.add_action(goal)
            states.append(new_state)

    def expand_event(self, goal, cur_state, states):

        # Need to reverse here for DFS like iteration
        KB_clauses = list(KB.get_clauses(goal))
        KB_clauses.reverse()

        if KB_clauses:
            for clause in KB_clauses:
                '''
                TODO: Actually resolving the temporal requirements correctly
                Simple replacement for now
                '''
                new_state = copy.deepcopy(cur_state)
                new_state.replace_event(goal, clause.reqs)
                states.append(new_state)

    def expand_fact(self, goal, cur_state, states):
        # Check if variables are needed

        # Need to reverse here for DFS like iteration
        subs = list(unify_fact(goal))
        subs.reverse()

        for sub in subs:
            new_state = copy.deepcopy(cur_state)
            # new_state.remove_first_goal()
            new_state.update_subs(sub)
            states.append(new_state)


# def backtrack_solve(start, cycle_time, cycle_actions, pos=0):


SOLVER = _Solver()
