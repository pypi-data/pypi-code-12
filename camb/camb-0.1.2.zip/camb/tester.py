import sys, platform, os
import os
from matplotlib import pyplot as plt
import numpy as np

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import camb
from camb import model, initialpower

pars = camb.set_params(H0=67.5, ombh2=0.022, omch2=0.122, As=2e-9, ns=0.95)
data = camb.get_background(pars)

eta = np.linspace(1, 400, 5)
ks = [0.02, 0.1]
ev = data.get_time_evolution(ks, eta, ['delta_baryon', 'delta_photon'])
print(ev[0, 0:5, 0])

_, axs = plt.subplots(1, 2, figsize=(12, 5))
for i, ax in enumerate(axs):
    ax.plot(eta, ev[i, :, 0])
    ax.plot(eta, ev[i, :, 1])
    ax.set_title('$k= %s$' % ks[i])
    ax.set_xlabel(r'$\eta/\rm{Mpc}$');
plt.legend([r'$\Delta_b$', r'$\Delta_\gamma$'], loc='upper left');

"""eta = np.linspace(1, 400, 20)
ks = [0.02,0.1]
ev = data.get_time_evolution(ks, eta, ['delta_baryon','delta_photon'])
_, axs= plt.subplots(1,2, figsize=(12,5))
for i, ax in enumerate(axs):
    ax.plot(eta,ev[i,:, 0])
    ax.plot(eta,ev[i,:, 1])
    ax.set_title('$k= %s$'%ks[i])
    ax.set_xlabel('$\eta$');
plt.legend([r'$\Delta_b$', r'$\Delta_\gamma$'], loc = 'upper left');
"""
plt.show()
