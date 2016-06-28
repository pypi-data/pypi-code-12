import memory_usage_notifier.memory_status as m

def checkStatus():
	m.returnCurrentMemoryUsage()

def startChecker():
	m.startMemoryConsumptionCheck()

