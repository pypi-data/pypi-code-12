#!/usr/bin/env python3
# _*_ coding:utf-8 _*_


def printList(lst, indent=False, level=0):
    for each in lst:
        if isinstance(each, list):
            printList(each, indent, level+1)
        else:
            if indent is True:
                for i in range(level):
                    print("\t", end="")
            print(each)
    return None
