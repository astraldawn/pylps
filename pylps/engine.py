import copy

from pylps.constants import *
from pylps.kb import KB
from pylps.solver import solve_multigoal, process_cycle_actions
from pylps.unifier import unify_conds, reify_goals, unify_obs


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
            KB.clear_cycle_actions()
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
        '''
        Work through the goals individually
        '''
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

            solve_multigoal(multigoal, self.current_time)

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


ENGINE = _ENGINE()
