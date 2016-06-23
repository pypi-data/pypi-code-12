# -*- coding:utf-8 -*-  
import multiprocessing
import multiprocessing.queues
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class multiProcessWork_frame():
    def __init__(self,class_of_process):
        self.class_of_process = class_of_process
        self.taskQueue = multiprocessing.queues.SimpleQueue() #建立任务队列
        self.processes = [] # 建立进程数组

    def once_work_helper(self,paraOfGetTaskList,process_para,numOfProcess):
        self.start_all_thread(numOfProcess)
        self.process_para = process_para
        self.set_all_processPara(process_para)
        self.input_tasks(self.getTaskList(paraOfGetTaskList))
        # self.wait_work_done()
        self.stop_all_thread()

    def once_work(self,paraOfGetTaskList,process_para=None,numOfProcess=1,log_dir = None):
        if log_dir:
            try:
                self.class_of_process.thread_log # check if the thread class support the log module , if not , raise a Exception
            except Exception,e:
                raise NameError('the thread class do not have log moudule')

        if log_dir:
            print 'working with logging in ' + str(log_dir)
            self.class_of_process.log_switch(True)
            self.class_of_process.start_log_dir(log_dir)
            self.once_work_helper(paraOfGetTaskList,process_para,numOfProcess)
            self.class_of_process.stop_log()
        else:
            print 'working without log ...'
            self.once_work_helper(paraOfGetTaskList,process_para,numOfProcess)

    def start_all_thread(self,numOfProcess):
        for threadID in range(1,numOfProcess+1):
            thread_ = self.class_of_process(self.taskQueue,threadID)
            thread_.start()
            self.processes.append(thread_)

    def stop_all_thread(self):
        while not self.taskQueue.empty(): # 等待队列被取空
            pass
        for t in self.processes:
            if t.dealingState():
                print 'waiting: thread ' + str(t.getID()) + ' with task of ' + str(t.process_taskQueue.get())
            while t.dealingState(): # 等待所有进程完成手中的活
                pass
            t.stop()
            t.join()

    def forceStop_all_thread(self):
        for t in self.processes:
            t.stop() # 给进程发出结束进程命令
            t.join() # 等待所有进程结束后，主进程再结束

    def wait_work_done(self):
        while not self.taskQueue.empty(): # 等待队列被取空
            pass
        for t in self.processes:
            if t.dealingState():
                print 'waiting: thread ' + str(t.getID()) + ' with task of ' + str(t.process_taskQueue.get())
            while t.dealingState(): # 等待所有进程完成手中的活
                pass

    def set_all_processPara(self,process_para):
        self.process_para = process_para
        for t in self.processes: #新任务队列开始前对每个进程进行参数设置
            t.setPara(process_para)

    def input_tasks(self,taskList):
        if len(taskList):
            for t in taskList:
                self.taskQueue.put(t)  # 向任务队列中添加任务
            # for n in range(len(taskList)):
            #     self.taskQueue.put(taskList[n]) 

    def getTaskList(paraOfGetTaskList):
        pass

    def getNextPara(para):
        pass