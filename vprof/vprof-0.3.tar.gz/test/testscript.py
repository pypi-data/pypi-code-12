import numpy
# import time
#
# foo = lambda x: x
#
# def t(arg):
#     if arg == 1:
#         # foo(1)
#         time.sleep(0.5)
#     else:
#         time.sleep(1)
#
#
# def lst1(size):
#     t(2)
#     t(2)
#     # return ['a' for _ in range(size)]
#
#
# def lst2(size):
#     t(1)
#     t(1)
#     # return ['a' for _ in range(size)]
#
#
# lst1(1000)
# lst2(2000)
#
# def prod(lst):
#     if not lst:
#         return 1
#     return lst[0] * prod(lst[1:])
#
# print(prod([1]))
# print(prod(list(range(1, 4))))
# # # print()
# # # print
# # # print()
# # #
# # #
# def foo():
#     pass
#     # for _ in range(200):
#         # x = 1
#
# def fib(n):
#     a, b = 0, 1
#     for _ in range(n):
#         foo()
#         yield a
#         a, b = b, a + b
#
# def main():
#     print(list(fib(100)))
#
# if __name__ == "__main__":
#     main()
#
#
# def bsearch(lst, el):
#     """Iterative binary search.
#         >>> bsearch([12, 15, 17, 19], 15)
#         1
#         >>> bsearch([1, 2, 3, 4], 3)
#         2
#         >>> bsearch([1, 3, 5, 8, 9, 11], 7)
#     """
#     start, end = 0, len(lst) - 1
#     while start < end:
#         mid = (start + end) // 2
#         if lst[mid] == el:
#             return mid
#         elif el > lst[mid]:
#             start = mid + 1
#         else:
#             end = mid
#
#
# def bsearchr(lst, el):
#     """Recursive binary search.
#         >>> bsearchr([12, 15, 17, 19], 15)
#         1
#         >>> bsearchr([1, 2, 3, 4], 3)
#         2
#         >>> bsearchr([1, 3, 5, 8, 9, 11], 7)
#     """
#     def _bsearchr(lst, el):
#         if len(lst) < 2:
#             raise StopIteration
#         mid = len(lst) // 2
#         if lst[mid] == el:
#             return mid
#         elif el > lst[mid]:
#             return _bsearchr(lst[:mid], el)
#         else:
#             return mid + _bsearchr(lst[mid:], el)
#
#     try:
#         return _bsearchr(lst, el)
#     except StopIteration:
#         return
#
#
# for i in range(250):
#     print(bsearchr([1, 2, 3, 4], 3))

#
# def insertion_sort(lst):
#     """ Implementation of insertion sort.
#         >>> insertion_sort([3, 2, 1, 5, 4])
#         [1, 2, 3, 4, 5]
#     """
#     for i, _ in enumerate(lst):
#         for j in range(i, 0, -1):
#             if lst[j] < lst[j - 1]:
#                 lst[j], lst[j - 1] = lst[j - 1], lst[j]
#             else:
#                 break
#     return lst
#
# print(insertion_sort(list(reversed(range(1000)))))

#
#
# def qsort(lst):
#     """Simplest implementation of quicksort.
#        >>> qsort([3, 4, 1, 5, 2, 9, 7, 6, 43, 11])
#        [1, 2, 3, 4, 5, 6, 7, 9, 11, 43]
#     """
#     if not len(lst):
#         return []
#     else:
#         pivot, other = lst[0], lst[1:]
#         lesser = qsort([el for el in other if el < pivot])
#         greater = qsort([el for el in other if el >= pivot])
#         return lesser + [pivot] + greater
#
#
# print(qsort([3, 4, 1, 5, 2, 9, 7, 6, 43, 11]))
#
# class DLLNode:
#     def __init__(self, value, prev=None, nnext=None):
#         self.value, self.prev, self.nnext = value, prev, nnext
#
#
# class DLL:
#     def __init__(self):
#         self.head, self.tail = None, None
#
#     def push_back(self, value):
#         if not self.head:
#             newnode = DLLNode(value)
#             self.head, self.tail = newnode, newnode
#         else:
#             newnode = DLLNode(value, prev=self.tail)
#             self.tail.nnext = newnode
#             self.tail = newnode
#
#     def push_front(self, value):
#         if not self.head:
#             newnode = DLLNode(value)
#             self.head, self.tail = newnode, newnode
#         else:
#             newnode = DLLNode(value, nnext=self.head)
#             self.head.prev = newnode
#             self.head = newnode
#
#     def __iter__(self):
#         current = self.head
#         while current:
#             yield current.value
#             current = current.nnext
#
#     def reverse(self):
#         first, last = self.tail, self.head
#         while first is not last:
#             first.value, last.value = last.value, first.value
#             first, last = first.prev, last.nnext


# import unittest
#
#
# class DLLUnittest(unittest.TestCase):
#     def setUp(self):
#         self.dll = DLL()
#
#     def testPushBack(self):
#         self.dll.push_back(1)
#         self.dll.push_back(3)
#         self.dll.push_back(5)
#         self.dll.push_back(7)
#         self.dll.push_back(9)
#         self.assertListEqual(list(self.dll), [1, 3, 5, 7, 9])
#
#     def testPushFront(self):
#         self.dll.push_front(1)
#         self.dll.push_front(3)
#         self.dll.push_front(5)
#         self.dll.push_front(7)
#         self.dll.push_front(9)
#         self.assertListEqual(list(self.dll), [9, 7, 5, 3, 1])
#
#     def testReverse(self):
#         self.dll.push_front(1)
#         self.dll.push_front(3)
#         self.dll.push_front(5)
#         self.dll.push_front(7)
#         self.dll.push_front(9)
#         self.dll.reverse()
#         self.assertListEqual(list(self.dll), [1, 3, 5, 7, 9])
#
#     def testMixed(self):
#         self.dll.push_front(1)
#         self.dll.push_back(3)
#         self.dll.push_front(5)
#         self.dll.push_back(7)
#         self.dll.push_back(9)
#         self.assertListEqual(list(self.dll), [5, 1, 3, 7, 9])


# if __name__ == "__main__":
# unittest.main()


import numpy
import pylab
import scipy.io

dataset = scipy.io.loadmat('test/ex7data2.mat')
x = dataset['X']

def euclidean_distance(x1, x2, y1, y2):
    return numpy.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

K = 2
EPS = 0.25
centroids = numpy.zeros((K, 2))
for i in range(K):
    rand_i = numpy.random.random_integers(x.shape[0] - 1)
    centroids[i] = x[rand_i]

distances = numpy.zeros((x.shape[0], K))
distance_delta = numpy.ones(K)
num_iter = 0
history = []
while (distance_delta >= EPS).all():
    # Calculate distance to centroids.
    for i in range(x.shape[0]):
        for j in range(K):
            distances[i, j] = euclidean_distance(
                x[i, 0], centroids[j, 0], x[i, 1], centroids[j, 1])
    # Pick closest cluster.
    point_clusters = distances.argmin(axis=1)
    history.append(point_clusters)
    for i in range(K):
        prev_cent_x, prev_cent_y = centroids[i, 0], centroids[i, 1]
        centroids[i, :] = numpy.average(x[point_clusters == i], axis=0)
        distance_delta[i] = euclidean_distance(
            prev_cent_x, centroids[i, 0], prev_cent_y, centroids[i, 1])
    num_iter += 1
print('Algorithm converged in %s iterations' % num_iter)
