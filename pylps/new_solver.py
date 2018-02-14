'''
Revised solver that will recursively yield solutions
'''
import copy
from collections import deque

from pylps.constants import *
from pylps.exceptions import *
from pylps.kb import KB

from pylps.tree_goal import TreeGoal
from pylps.state import State

from pylps.unifier import unify_fact
from pylps.solver import solve_multigoal
from pylps.solver_utils import process_cycle_actions


class _Solver(object):

    def __init__(self):
        self.current_time = None

    def solve_goals(self, current_time):
        '''
        Entry point, attempt to solve reactive rules
        Note that reactive rules R1 .. RN are not ANDs
        '''
        self.current_time = current_time

        solved_group = set()

        cur_goal_pos = 0

        KB_goals = KB.goals.children

        states = set()

        backtracking = True
        backtracking_counter = 1

        while(cur_goal_pos < len(KB_goals)):
            multigoal = KB_goals[cur_goal_pos]

            if multigoal in solved_group:
                multigoal.update_result(G_SOLVED)
                cur_goal_pos += 1
                continue

            # solve_multigoal(multigoal, current_time)

            # print(self.backtrack_solve(multigoal))
            solutions = self.backtrack_solve(multigoal)

            print(next(solutions))

            # DEBUG
            return

            if KB.goals not in states:
                states.add(copy.deepcopy(KB.goals))
            else:
                # print(KB.goals)
                # print('DUPLICATE STATE')
                cur_goal_pos += 1
                continue

            if multigoal.result in SOLVED_RESPONSES:
                solved_group.add(multigoal)
                backtracking_counter = 1

            if multigoal.result is G_CLAUSE_FAIL:  # Go back one
                prev_pos = cur_goal_pos - backtracking_counter

                if prev_pos < 0:
                    backtracking_counter = 1
                    multigoal.update_result(G_DISCARD)
                    cur_goal_pos += 1
                    continue

                prev_goal = KB_goals[prev_pos]
                solved_group.remove(prev_goal)
                prev_goal.reset(propagate=True)
                backtracking_counter += 1
                continue

            cur_goal_pos += 1
            # print(multigoal.result, cur_goal_pos)
            # print(goal_stk)

        # print(KB.goals)
        max_solved = 0
        for state in states:
            # print(self.current_time, state._to_tuple())
            solved = 0
            for child in state.children:
                if child.result in SOLVED_RESPONSES:
                    solved += 1

            if solved > max_solved:
                KB.set_goals(state)
                max_solved = solved

        if KB.goals:
            # KB.display_cycle_actions()
            new_children = []
            for child in KB.goals.children:
                if (child.result in SOLVED_RESPONSES or
                        child.result is G_DISCARD):
                    continue
                # if(child.result in SOLVED_RESPONSES or
                #         child.result is G_DISCARD):
                #     continue
                elif child.result is G_FAIL_NO_SUBS:
                    child.reset(propagate=True)
                new_children.append(child)

            KB.set_children(new_children)
            # print(KB.goals)
            process_cycle_actions()

    def backtrack_solve(self, start: TreeGoal, pos=0):
        '''
        AND step of solving
        Solve all inside here, except for the case when deferring
        This function should return a generator
        '''
        self.states = deque()

        s_goals = deque([child.goal for child in start.children])
        s_subs = start.subs
        start_state = State(s_goals, s_subs)
        self.states.append(start_state)

        while self.states:
            cur_state = self.states.popleft()

            # Nothing left
            if not cur_state.goals:
                yield cur_state

            else:

                goal = cur_state.goals[0]
                self.expand_goal(goal, cur_state)

    def expand_goal(self, goal, cur_state):

        try:
            goal_obj = goal[0]
            # self._temporal_vars = tuple(
            #     var(temporal_var.name)
            #     for temporal_var in goal[1:]
            # )
        except TypeError:
            goal_obj = goal
            # self._temporal_vars = None

        if goal_obj.BaseClass is ACTION:
            self.expand_action(goal, cur_state)
        elif goal_obj.BaseClass is FACT:
            # Check if a sub is needed
            self.expand_fact(goal, cur_state)

    def expand_action(self, goal, cur_state):
        try:
            goal_obj = goal[0]
        except TypeError:
            goal_obj = goal

        new_state = copy.deepcopy(cur_state)
        new_state.remove_first_goal()
        new_state.add_action(goal_obj)
        self.states.append(new_state)

    def expand_fact(self, goal, cur_state):
        # Check if variables are needed
        try:
            goal_obj = goal[0]
        except TypeError:
            goal_obj = goal

        for sub in unify_fact(goal_obj):
            new_state = copy.deepcopy(cur_state)
            new_state.remove_first_goal()
            new_state.update_subs(sub)
            self.states.append(new_state)

    # def solve_single(self, cur: TreeGoal):
    #     goal = self._extract_goal(cur)
    #     print(goal)

    #     if goal.BaseClass is ACTION:
    #         # print('WE ARE HERE')
    #         return [{'X': 'TEST DEBUG'}]
    #     elif goal.BaseClass is FACT:
    #         unify_fact_gen = unify_fact(goal)
    #         return unify_fact_gen
    #     else:
    #         raise UnimplementedOutcomeError(goal.BaseClass)

    def _extract_goal(self, tree_goal: TreeGoal):
        if tree_goal.temporal_vars:
            return tree_goal.goal[0]

        return tree_goal.goal


SOLVER = _Solver()
