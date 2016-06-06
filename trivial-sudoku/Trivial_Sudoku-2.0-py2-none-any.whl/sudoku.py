#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2016 Alexandre Syenchuk (alexpirine)

import copy

ASCII_BOARD_TPL = """
+---+---+---+
|   |   |   |
|   |   |   |
|   |   |   |
+---+---+---+
|   |   |   |
|   |   |   |
|   |   |   |
+---+---+---+
|   |   |   |
|   |   |   |
|   |   |   |
+---+---+---+
""".strip()

class Sudoku(object):
    def __init__(self, matrix):
        self.board = list(matrix)
        self.moves = [set() if v else set(range(1,10)) for v in self.board]
        self.unsolved = set([k for k, v in enumerate(self.board) if not v])
        self.solved = set([k for k, v in enumerate(self.board) if v])
        self._eliminate_all_bad_moves()

    @property
    def ascii(self):
        return ASCII_BOARD_TPL.replace(' ', '%d') % tuple(self.board)

    def _mark_solved(self, p, v):
        self.board[p] = v
        self.moves[p].clear()
        self.unsolved.remove(p)
        self.solved.add(p)

    def _get_row(self, p):
        start = p / 9 * 9
        return set(start + c for c in xrange(9))

    def _get_col(self, p):
        start = p % 9
        return set(start + r for r in xrange(0,81,9))

    def _get_box(self, p):
        start = p / 27 * 27 + p % 9 / 3 * 3
        return set(start + 9 * r + c for r in xrange(3) for c in xrange(3))

    def _get_influence(self, p):
        return set.union(self._get_row(p), self._get_col(p), self._get_box(p)) - set([p]) - self.solved

    def _eliminate_bad_moves(self, p):
        for i in self._get_influence(p):
            self.moves[i] -= set([self.board[p]])
            if len(self.moves[i]) == 1:
                self._mark_solved(i, self.moves[i].pop())
                self._eliminate_bad_moves(i)

    def _eliminate_all_bad_moves(self):
        for s in self.solved.copy():
            self._eliminate_bad_moves(s)

    def _set_uniques_in_area(self):
        for value in xrange(1, 10):
            for get_area in [lambda a: self._get_row(a * 9), lambda a: self._get_col(a % 9), lambda a: self._get_box(a / 3 * 27 + a % 3 * 3)]:
                for a in range(9):
                    possible_positions = filter(lambda i: value in self.moves[i], get_area(a) - self.solved)
                    if len(possible_positions) == 1:
                        self._mark_solved(possible_positions[0], value)
                        self._eliminate_bad_moves(possible_positions[0])

    def solve(self):
        prev_unsolved = 0
        while prev_unsolved != len(self.unsolved):
            prev_unsolved = len(self.unsolved)
            self._set_uniques_in_area()
        for p in self.unsolved:
            for possible_value in self.moves[p]:
                test_problem = copy.deepcopy(self)
                test_problem._mark_solved(p, possible_value)
                solution = test_problem.solve()
                if solution:
                    return solution
            return False
        return self
