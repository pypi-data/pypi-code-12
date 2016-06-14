# -*- coding: utf-8 -*-

"""Delimmited ast : ast nodes produced ast.parse(text)
only contains lineno and offset values, that represents
the start of ast node in the text being pased.
The astd.parse will return a modified ast tree with
to_line and to_offset values"""

import ast


def parse(text):
    """parse ast delimmited text"""
    try:
        tree = ast.parse(text)
        l = ['0'] + text.splitlines()
        __process_node(tree, l)
        return tree
    except Exception as inst:
        import traceback
        import sys
        traceback.print_exc(file=sys.stdout)
        print type(inst)     # the exception instance
        print inst.args      # arguments stored in .args
        print inst
        raise inst


def __cutoff_node(node, to_lineno, to_col_offset):
    """Cut node lengths"""
    if hasattr(node, 'lineno'):
        if hasattr(node, 'to_lineno'):
            if node.to_lineno < to_lineno:
                return
            if node.to_lineno == to_lineno and node.to_col_offset <= to_col_offset:
                return
        setattr(node, 'to_lineno', to_lineno)
        setattr(node, 'to_col_offset', to_col_offset)
    for cur in ast.iter_child_nodes(node):
        __cutoff_node(cur, to_lineno, to_col_offset)


def __process_node(node, l):
    """Compute offsets"""
    prev = None
    for cur in ast.iter_child_nodes(node):
        if hasattr(cur, 'lineno'):
            __process_node(cur, l)
        if type(cur) is ast.Str:
            s = cur.s
            if s:
                if s[0] == '"':
                    s = s[1:]
                if s and s[-1] == '"':
                    s = s[:-1]
                v = (s + ' ').splitlines()
                v[-1] = v[-1][:-1]
                if len(v) > 1 and not v[0]:
                    del v[0]
            else:
                v = ['']
            n = len(v)
            if cur.col_offset >= 0:
                left_lin = cur.lineno
                left_qpos = l[left_lin].find('"""', cur.col_offset)
                if left_qpos < 0:
                    left_qpos = l[left_lin].find("'''", cur.col_offset)
                if left_qpos < 0:
                    dpos = l[left_lin].find('"', cur.col_offset)
                    spos = l[left_lin].rfind("'", cur.col_offset)
                    if dpos > spos:
                        left_qpos = dpos
                    else:
                        left_qpos = spos
                    left_pos = left_qpos + 1
                else:
                    left_pos = left_qpos + 3
            else:
                left_lin = cur.lineno - n + 1
                if v[0]:
                    left_pos = l[left_lin].rfind(v[0])
                else:
                    left_pos = 0
                while left_pos == 0:
                    left_lin = left_lin - 1
                    left_pos = len(l[left_lin])
                left_qpos = l[left_lin].rfind('"""')
                if left_qpos < 0:
                    left_qpos = l[left_lin].rfind("'''")
                if left_qpos < 0:
                    dpos = l[left_lin].rfind('"')
                    spos = l[left_lin].rfind("'")
                    if dpos > spos:
                        left_qpos = dpos
                    else:
                        left_qpos = spos
                    left_pos = left_qpos + 1
                else:
                    left_pos = left_qpos + 3
            right_lin = cur.lineno
            if v[-1]:
                if cur.col_offset > -1:
                    right_pos = l[right_lin].find(v[-1], cur.col_offset) + len(v[-1])
                else:
                    right_pos = l[right_lin].find(v[-1]) + len(v[-1])
            else:
                right_pos = 0
            while len(l[right_lin]) == 0:
                right_lin = right_lin + 1
                right_pos = 0
            right_qpos = l[right_lin].find('"""', right_pos) + 3
            if right_qpos < 3:
                right_qpos = l[right_lin].find("'''", right_pos) + 3
            if right_qpos < 3:
                dpos = l[right_lin].find('"')
                spos = l[right_lin].find("'")
                if dpos > 0 and dpos < spos:
                    right_qpos = dpos
                else:
                    right_qpos = spos
                right_pos = right_qpos - 1
            else:
                right_pos = right_qpos - 3

            setattr(cur, 'to_lineno', right_lin)
            setattr(cur, 'to_col_offset', right_pos)
            cur.lineno = left_lin
            cur.col_offset = left_pos
            if type(node) is ast.Expr:
                node.lineno = left_lin
                node.col_offset = left_qpos
                node.to_lineno = right_lin
                node.to_col_offset = right_qpos

        if hasattr(cur, 'lineno'):
            if prev:
                #find previous non empty
                lin = cur.lineno
                pos = cur.col_offset
                while True:
                    while pos and l[lin][pos - 1:pos].isspace():
                        pos = pos - 1
                    if pos == 0:
                        lin = lin - 1
                        while len(l[lin].strip()) == 0 or l[lin].strip()[0] == '#':
                            lin = lin - 1
                        pos = len(l[lin])
                    else:
                        __cutoff_node(prev, lin, pos)
                        break
        prev = cur
    if prev:
        if hasattr(node, 'to_lineno'):
            lin = node.to_lineno
            pos = node.to_col_offset
        else:
            lin = len(l) - 1
            pos = len(l[lin])
        while True:
            while pos and l[lin][pos - 1:pos].isspace():
                pos = pos - 1
            if pos == 0:
                lin = lin - 1
                pos = len(l[lin])
            else:
                __cutoff_node(prev, lin, pos)
                break

