from multiprocessing import Process

def run_multi(_datas, _process_cnt, _process):
	for p_order in range(0, _process_cnt):
		new_p = Process(target=run_process, args=(_datas, p_order, _process_cnt, _process))
		new_p.start()
		print "process %d is start!" % (p_order)

def run_process(_datas, _process_number, _process_offset, _process):
	task_cnt = len(_datas)
	task_index = _process_number

	while task_index < task_cnt:
		_process(_datas[task_index], task_index)
		print "%d / %d" % (task_index+1, task_cnt)
		task_index += _process_offset

	print "process %d is end!" % (_process_number)