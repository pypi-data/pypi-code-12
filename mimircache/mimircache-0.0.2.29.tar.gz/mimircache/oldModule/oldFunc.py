


def _cal_log_num(self, max_rd, length):
    """
    find out the LOG_NUM that makes the number of pixels in y axis to match the number of pixels in x axis
    :param max_rd: maxinum reuse distance
    :param length: length of break points (also number of pixels along x axis)
    :return:
    """
    init_log_num = 10
    l2_prev = length
    while True:
        l2 = math.log(max_rd, init_log_num)
        if l2 > length > l2_prev:
            return init_log_num
        l2_prev = l2
        init_log_num = (init_log_num - 1) / 2 + 1


@staticmethod
def _get_breakpoints_virtualtime(bin_size, total_length):
    """

    :param bin_size: the size of the group (virtual time slice)
    :param total_length: the total length of trace requests
    :return: a list of break points

    """
    break_points = []
    assert total_length // bin_size > 10, "bin size too large, please choose a smaller one, " \
                                          "total length %d, bin size %d" % (total_length, bin_size)
    for i in range(total_length // bin_size):
        break_points.append(i * bin_size)
    if break_points[-1] != total_length - 1:
        break_points.append(total_length - 1)

    if (len(break_points)) > 10000:
        colorfulPrintWithBackground('yellow', 'blue', "number of pixels in one dimension are more than 10000, \
        exact size: %d, it may take a very long time, if you didn't intend to do it, \
        please try with a larger time stamp" % len(break_points))

    return break_points


@staticmethod
def _get_breakpoints_realtime(reader, interval):
    """
    given reader(vscsi) and time interval, split the data according to the time interval,
    save the order into break_points(list)
    :param reader:
    :param interval:
    :return:
    """
    reader.reset()
    break_points = []
    prev = 0
    for num, line in enumerate(reader.lines()):
        if (float(line[0]) - prev) > interval:
            break_points.append(num)
            prev = float(line[0])

    # noinspection PyUnboundLocalVariable
    if line[0] != prev:
        # noinspection PyUnboundLocalVariable
        break_points.append(num)

    if (len(break_points)) > 10000:
        colorfulPrintWithBackground('yellow', 'blue', "number of pixels in one dimension are more than 10000, \
        exact size: %d, it may take a very long time, if you didn't intend to do it, \
        please try with a larger time stamp" % len(break_points))

    # print(break_points)
    return break_points


@staticmethod
def _calc_hit_rate(reuse_dist_array, last_access_dist_array, cache_size, begin_pos, end_pos):
    """
    the original function for calculating hit rate, given the reuse_dist_array, cache_size,
    begin position and end position in the reuse_dist_array, return hit rate
    now isolate as a separate function
    :param reuse_dist_array:
    :param cache_size:
    :param begin_pos:
    :param end_pos:
    :return:
    """
    hit_count = 0
    miss_count = 0
    for i in range(begin_pos, end_pos):
        if reuse_dist_array[i] == -1:
            # never appear
            miss_count += 1
            continue
        if last_access_dist_array[i] - (i - begin_pos) <= 0 and reuse_dist_array[i] < cache_size:
            # hit
            hit_count += 1
            print("{}: {}".format(i, reuse_dist_array[i]))
        else:
            # miss
            miss_count += 1
    print("hit={}, hit+miss={}, total size:{}, hit rate:{}".format(hit_count, hit_count + miss_count,
                                                                   end_pos - begin_pos,
                                                                   hit_count / (end_pos - begin_pos)))
    return hit_count / (end_pos - begin_pos)

