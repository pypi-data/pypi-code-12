import time
class timing:
   def __init__(self,info):
      self.info=info
      self.t0=time.clock()
      self.w0=time.time()
      self.t1=None
      self.w1=None
   def __str__(self):
      if self.t1 is None: self.stop()
      t=self.t1-self.t0
      w=self.w1-self.w0
      return "Time used in %-20s:%10.2f (cpu) %10.2f (wall)"""%(self.info,t,w)
   def stop(self):
      self.t1=time.clock()
      self.w1=time.time()
