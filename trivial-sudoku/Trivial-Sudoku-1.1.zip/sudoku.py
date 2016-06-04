#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2016 Alexandre Syenchuk (alexpirine)

import copy

class SudokuProblem(object):
    def __init__(self, matrix):
        self.matrix = list()
        self.field = list()
        for x in range(9):
            self.matrix.append(list())
            self.field.append(list())
            for y in range(9):
                self.matrix[x].append(matrix[x][y])
                if not matrix[x][y]:
                    self.field[x].append(set(range(1,10)))
                else:
                    self.field[x].append(set())

    def print_matrix(self):
        for k in range(9):
            if not k % 3:
                print '+' + ('-'*3 + '+')*3
            print ''.join([('' if i % 3 else '|') + ('%d' % v if v else ' ') for i, v in enumerate(self.matrix[k])]) + '|'
        print '+' + ('-'*3 + '+')*3

    @staticmethod
    def get_in_col_idx(x, y, k=0):
        return (x + k) % 9, y

    @staticmethod
    def get_in_row_idx(x, y, k=0):
        return x, (y + k) % 9

    @staticmethod
    def get_in_cell_idx(x, y, k=0):
        return x / 3 * 3 + (x + k / 3) % 3, y / 3 * 3 + (y + k) % 3

    def get_in_col(self, matrix_type, x, y, k=0):
        x, y = self.get_in_col_idx(x, y, k)
        return getattr(self, matrix_type)[x][y]

    def get_in_row(self, matrix_type, x, y, k=0):
        x, y = self.get_in_row_idx(x, y, k)
        return getattr(self, matrix_type)[x][y]

    def get_in_cell(self, matrix_type, x, y, k=0):
        x, y = self.get_in_cell_idx(x, y, k)
        return getattr(self, matrix_type)[x][y]

    def set_in_col(self, matrix_type, value, x, y, k=0):
        x, y = self.get_in_col_idx(x, y, k)
        getattr(self, matrix_type)[x][y] = value

    def set_in_row(self, matrix_type, value, x, y, k=0):
        x, y = self.get_in_row_idx(x, y, k)
        getattr(self, matrix_type)[x][y] = value

    def set_in_cell(self, matrix_type, value, x, y, k=0):
        x, y = self.get_in_cell_idx(x, y, k)
        getattr(self, matrix_type)[x][y] = value

    def set_possible_values(self, x, y):
        impossible_values = set()
        for k in range(1, 9):
            # filter out column values
            impossible_values.add(self.get_in_col('matrix', x, y, k))
            # filter out row values
            impossible_values.add(self.get_in_row('matrix', x, y, k))
            # filter out cell values
            impossible_values.add(self.get_in_cell('matrix', x, y, k))
        self.field[x][y] -= impossible_values
        if len(self.field[x][y]) == 1:
            self.matrix[x][y] = self.field[x][y].pop()
            return True
        else:
            return False

    def set_cell_values(self, n):
        x, y = n / 3 * 3, n % 3 * 3
        advanced = False
        for v in range(1, 10):
            appearances = 0
            for k in range(9):
                if v in self.get_in_cell('field', x, y, k):
                    appearances += 1
                    index = k
            if appearances == 1:
                self.get_in_cell('field', x, y, index).clear()
                self.set_in_cell('matrix', v, x, y, index)
                advanced = True
        return advanced

    def set_row_values(self, n):
        x, y = n, 0
        advanced = False
        for v in range(1, 10):
            appearances = 0
            for k in range(9):
                if v in self.get_in_row('field', x, y, k):
                    appearances += 1
                    index = k
            if appearances == 1:
                self.get_in_row('field', x, y, index).clear()
                self.set_in_row('matrix', v, x, y, index)
                advanced = True
        return advanced

    def set_col_values(self, n):
        x, y = 0, n
        advanced = False
        for v in range(1, 10):
            appearances = 0
            for k in range(9):
                if v in self.get_in_col('field', x, y, k):
                    appearances += 1
                    if appearances > 2:
                        # don't bother finding other possible locations, 2 is already too much
                        break
                    index = k
            if appearances == 1:
                self.get_in_col('field', x, y, index).clear()
                self.set_in_col('matrix', v, x, y, index)
                advanced = True
        return advanced

    def heuristic1(self):
        advances = 0
        advanced = True
        while advanced:
            advanced = False
            for x in range(9):
                for y in range(9):
                    if self.matrix[x][y] != 0:
                        continue
                    self.set_possible_values(x, y)
                    if self.matrix[x][y] != 0:
                        advanced = True
                        advances += 1
        return advances

    def heuristic2(self):
        for n in range(9):
            if self.set_cell_values(n) or self.set_row_values(n) or self.set_col_values(n):
                return True
        return False

    def solve(self):
        advanced = True
        while advanced:
            advanced = False
            if self.heuristic1():
                advanced = True
            if self.heuristic2():
                advanced = True
        for pos in range(9*9):
            x, y = pos / 9, pos % 9
            if self.matrix[x][y] != 0:
                continue
            for possible_value in self.field[x][y]:
                test_problem = copy.deepcopy(self)
                test_problem.matrix[x][y] = possible_value
                test_problem.field[x][y].clear()
                solution = test_problem.solve()
                if solution:
                    return solution
            return False
        return self
