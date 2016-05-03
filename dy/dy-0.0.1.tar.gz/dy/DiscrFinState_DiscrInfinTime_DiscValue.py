from __future__ import print_function
from numpy import allclose, array, identity, zeros
from numpy.linalg import inv
from pandas import DataFrame


class Prob:
    def __init__(
            self,
            nb_states=1,
            state_transition_prob_matrix_func=lambda policy: array([[1.]]),
            expected_values_per_stage_func=lambda policy: array([[0.]]),
            discount_factor=.999,
            bellman_op=lambda terminal_expected_value: array([[0.]])):
        self.nb_states = nb_states
        self.state_transition_prob_matrix_func = state_transition_prob_matrix_func
        self.expected_values_per_stage_func = expected_values_per_stage_func
        self.discount_factor = discount_factor
        self.bellman_op = bellman_op

    def expected_values(self, policy):
        return inv(identity(self.nb_states) -
                   self.discount_factor * self.state_transition_prob_matrix_func(policy))\
            .dot(self.expected_values_per_stage_func(policy))

    def value_iteration(self, init_values=None, rtol=1e-5, atol=1e-8):
        if init_values:
            curr_values = init_values
        else:
            curr_values = zeros((self.nb_states, 1))
        prev_values = None
        i = 0
        print('Running Value Iteration #', end='')
        while (prev_values is None) or (not allclose(curr_values, prev_values, rtol=rtol, atol=atol)):
            i += 1
            print(i, end=', ')
            prev_values = curr_values.copy()
            curr_values = self.bellman_op(terminal_expected_values=prev_values, return_policy=False)
        print('done!')
        d = DataFrame(dict(control=tuple(self.bellman_op(terminal_expected_values=curr_values, return_policy=True))))
        d['expected_value'] = curr_values.flatten()
        return d

    def relative_value_iteration(self, rtol=1e-5, atol=1e-8):
        pass

    def q_factor_value_iteration(self):
        pass

    def policy_iteration(self, init_policy=None):
        if init_policy:
            curr_policy = init_policy
        else:
            curr_policy = self.nb_states * (0,)
        prev_policy = None
        identity_matrix = identity(self.nb_states)
        cached_matrix_inverses = {}
        i = 0
        print('Running Policy Iteration #', end='')
        while (prev_policy is None) or (curr_policy != prev_policy):
            i += 1
            print(i, end=', ')
            prev_policy = curr_policy
            if prev_policy in cached_matrix_inverses:
                matrix_inverse = cached_matrix_inverses[prev_policy]
            else:
                matrix_inverse = \
                    inv(identity_matrix - self.discount_factor * self.state_transition_prob_matrix_func(prev_policy))
                cached_matrix_inverses[prev_policy] = matrix_inverse
            expected_values = matrix_inverse.dot(self.expected_values_per_stage_func(prev_policy))
            curr_policy = tuple(self.bellman_op(terminal_expected_values=expected_values, return_policy=True))
        print('done!')
        d = DataFrame(dict(control=curr_policy))
        d['expected_value'] = expected_values.flatten()
        return d

    def q_factor_policy_iteration(self):
        pass
