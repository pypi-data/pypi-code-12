from mimircache.cacheReader.vscsiReader import vscsiCacheReader
from mimircache.cacheReader.csvReader import csvCacheReader
from pymining import itemmining
from collections import deque
import sys
import pickle
from multiprocessing import Process, Pool


def test1(fname, group_size, min_support):
    l = deque()
    transactions = []
    line = 0
    with open(fname, 'r') as ifile:
        flag = True
        while flag:
            while line < group_size:
                e = ifile.readline().strip(' \n\t\r')
                if not e:
                    flag = False
                    break
                l.append(e)
                line += 1
            transactions.append(tuple(l))
            l.clear()
            line = 0

    print(len(transactions))
    print("memory: " + str(sys.getsizeof(transactions)))
    # transactions = [('a', 'b', 'c'), ('b'), ('a'), ('a', 'c', 'd'), ('b', 'c'), ('b', 'c')]
    # itemmining.


    relim_input = itemmining.get_relim_input(transactions)
    report = itemmining.relim(relim_input, min_support=min_support)
    for i, j in report.items():
        print(str(i) + ': ' + str(j))

    with open("../data/mining.dat", 'w') as ofile:
        for i in report.keys():
            ofile.write(','.join(i) + '\n')


        # print(report)
        # with open(fname + '_r2', 'wb') as ofile:
        # 	pickle.dump(report, ofile)


def test2(fname, time_interval, min_support, filename="../data/minming.dat"):
    # reader  = vscsiCacheReader(fname)
    reader  = csvCacheReader(fname, 3, delimiter=', ')

    break_points = _get_breakpoint_list_timestamp(reader, time_interval)


    l = deque()
    transactions = []
    line = 0
    pos_in_break_points = 1
    for num, lbn in enumerate(reader):
        if num == break_points[pos_in_break_points]:
            transactions.append(tuple(l))
            l.clear()
            l.append(lbn)
            pos_in_break_points += 1
            continue
        else:
            l.append(lbn)

    # print("all transactions: {}".format(transactions))

    print("number of transactions: %d"%len(transactions))

    print("memory: " + str(sys.getsizeof(transactions)))
    # transactions = [('a', 'b', 'c'), ('b'), ('a'), ('a', 'c', 'd'), ('b', 'c'), ('b', 'c')]
    # itemmining.


    relim_input = itemmining.get_relim_input(transactions)
    report = itemmining.relim(relim_input, min_support=min_support)
    # for i, j in report.items():
    #     print(str(i) + ': ' + str(j))

    with open(filename, 'w') as ofile:
        for i in report.keys():
            ofile.write(','.join(i) + '\n')


        # print(report)
        # with open(fname + '_r2', 'wb') as ofile:
        # 	pickle.dump(report, ofile)


def _get_breakpoint_list_timestamp(reader, time_interval):
    # generate break point
    break_points = []
    prev = 0
    for num, line in enumerate(reader.lines()):
        if (int(line[0])-prev) > time_interval:
            break_points.append(num)
            prev = int(line[0])
    if line[0] != prev:
        break_points.append(num)
    # print(num)
    # print(break_points)
    # print(len(break_points))

    if (len(break_points))>10000:
        print("number of groups more than 10000, exact size: %d, it may be too slow"%len(break_points))
    reader.reset()
    return break_points







def a(c):
    print(c)


if __name__ == "__main__":
    import os
    if not os.path.exists('../data/mining'):
        os.makedirs('../data/mining/')
    l1 = [1000*(3**i) for i in range(16)]
    l2 = [10*i*i for i in range(1, 20)]
    process_list = []
    num_of_process = 0
    l3 = []
    for i in l1:
        for j in l2:
            l3.append(("../1a1a11a/for_mining", i, j, "../data/mining/"+str(i)+'_'+str(j)))
            continue
            if num_of_process<45:
                print("{}: {}".format(i, j))
                p = Process(target=test2, args=("../1a1a11a/for_mining", i, j, "../data/mining/"+str(i)+'_'+str(j)))
                p.start()
                process_list.append(p)
                num_of_process += 1
            else:
                pass
    print(l3)
    with Pool(processes=48) as p:
        for i in p.starmap(test2, l3):
            pass


    # print('\n'*12)
    # test1('../1a1a11a/for_mining', 1000, 1000)
