from brian2 import *
set_device('cpp_standalone', build_on_run=False)
group = NeuronGroup(1, 'dv/dt = -v/(10*ms) : 1')
group.v = 1
mon = StateMonitor(group, 'v', record=0)
run(5*ms)
group.active = False
run(5*ms)
device.build()

plot(mon.t/ms, mon[0].v)
show()
