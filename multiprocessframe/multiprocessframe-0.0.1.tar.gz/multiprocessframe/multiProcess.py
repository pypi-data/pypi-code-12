# -*- coding:utf-8 -*-  
import multiprocessing
import multiprocessing.queues
import sys,time
reload(sys)
sys.setdefaultencoding("utf-8")


class class_multiprocess(multiprocessing.Process):
    def __init__(self,queue,ID): # 初始化传入公共的任务队列和锁，进程ID
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.ID = ID
        self.isDealingLock = multiprocessing.Lock()
        self.exit_value = multiprocessing.Value('i',0)
        self.isDealing = multiprocessing.Value('i',0) # 初始化进程为空闲状态
        self.processPara = multiprocessing.queues.SimpleQueue()
        self.process_taskQueue = multiprocessing.queues.SimpleQueue()

    def run_standard(self):
        print 'Process '+str(self.ID)+' started ...'
        result_list = []
        while not self.exit_value.value: 
            if not self.queue.empty(): # 如果任务队列不空，则取一条任务
                taskPara = self.queue.get()
                self.process_taskQueue.put(taskPara)
                if not self.processPara.empty():
                    processPara = self.processPara.get()
                    processPara_full = self.getProcessPara_full(processPara)
                self.isDealing.value = 1 # 设定进程为工作状态
            else:
                continue
            self.isDealingLock.acquire() # 获取任务执行锁
            result = self.dealFunc(taskPara,processPara_full) # 传入任务参数，进入任务处理函数
            result_list.append(result)
            while not self.process_taskQueue.empty():
                self.process_taskQueue.get()
            self.isDealing.value = 0 # 设定进程为空闲状态
            taskPara = None # 设置taskPara为无
            self.isDealingLock.release() # 释放任务执行锁
        print 'Process '+str(self.ID)+' stopped ...'
        return result_list

    def run(self):
        result_list = self.run_standard()

    def stop(self): # 设定任务结束标志
        self.exit_value.value = 1

    def dealingState(self): #返回进程工作状态
        return self.isDealing.value

    def setPara(self,processPara): #进程参数配置
        self.isDealingLock.acquire()  # 获取任务执行锁
        self.setPara_handler(processPara)
        self.isDealingLock.release() # 释放任务执行锁

    def setPara_handler(self,processPara):
        while not self.processPara.empty():
            self.processPara.get()
        # print 'in putting in processPara'
        self.processPara.put(processPara)
        # print 'putted'
        # print 'setting processPara : ',processPara[1]
        # self.processPara = multiprocessing.Array('c',processPara)

    def getTaskPara(self): # 获取进程正在处理的任务参数
        return self.taskPara

    def getProcessPara_full(self,processPara):
        return processPara

    def getID(self): # 获取进程ID
        return self.ID

    def dealFunc(self,taskPara,processPara): # 任务处理函数
        return None