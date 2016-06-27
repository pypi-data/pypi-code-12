import time
import Pyro4.core

s = Pyro4.core.Proxy("PYRO:rpc@localhost:7766")

p = 0
while True:
    time.sleep(0.5)
    p = s.next_prime(p)
    print(p)
