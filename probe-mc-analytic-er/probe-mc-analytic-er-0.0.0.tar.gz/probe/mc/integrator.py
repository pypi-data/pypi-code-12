import numpy as np
from scipy.integrate import ode
import scipy.constants as C
from math import sqrt, log
import random
import math
import probe.mc.mc
import logging
import multiprocessing

random.seed()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.propagate = False


class Integrator(multiprocessing.Process):

    def __init__(self, particle=None, T=None, er_C=None, integrator_type='dopri5', geom='spher', p=None,
                 Tg=None, mg=None, rd=None, npar=10000, show_progress_every_par=1000, queue=None, iproc=0,
                 rdd=None):

        multiprocessing.Process.__init__(self)

        assert particle in ['el', 'ari']
        assert geom in ['spher']
        assert er_C is not None
        assert p is not None
        assert Tg is not None
        assert T is not None
        assert rd is not None
        assert mg is not None

        self.particle = particle
        self.rd = rd
        self.rdd = rdd
        self.T = T

        # neutral gas
        self.p = p
        self.Tg = Tg
        self.mg = mg
        self.ng = self.p / (C.k * self.Tg)
        self.sigmag = math.sqrt(C.k * self.Tg / self.mg)

        if particle == 'el':
            self.m = C.m_e
            self.q = -C.e
            self.sigma_cs = 6e-20
            self.VmaxElectronCollision = 5e6
            self.cross_const = self.sigma_cs * self.VmaxElectronCollision

        if particle == 'ari':
            self.m = 39.944 * C.m_u - C.m_e
            self.q = C.e
            self.cross_const = 4.6e-16

        self.q_o_m = self.q / self.m

        if geom == 'spher':
            self.solver = ode(Integrator.spher_analytic_er)
            self.solver.set_integrator(integrator_type)
            self.solver.set_f_params(self.q_o_m, er_C)

        self.A = self.m / (2.0 * C.k * self.T)
        self.mean_velocity = sqrt(1.0 / self.A)
        self.sigma = sqrt(1.0 / (2.0 * self.A))

        self.npar = npar
        self.show_progress_every_par = show_progress_every_par
        self.queue = queue
        self.iproc = iproc

    def __str__(self):
        return ('particle: {}\n'.format(self.particle)+
                'rd: {}\n'.format(self.rd)+
                'T: {}\n'.format(self.T)+
                'p: {}\n'.format(self.p)+
                'Tg: {}\n'.format(self.Tg)+
                'ng: {}\n'.format(self.ng)+
                'm: {}\n'.format(self.m)+
                'q: {}\n'.format(self.q)+
                'cross_const: {}\n'.format(self.cross_const)+
                'q_o_m: {}\n'.format(self.q_o_m)+
                'A: {}\n'.format(self.A)+
                'mean_velocity: {}\n'.format(self.mean_velocity)+
                'sigma: {}\n'.format(self.sigma))

    def _next_coll_time(self):
        while True:
            yield -log(random.random()) / (self.cross_const * self.ng)

    def _next_new_position_iterator(self):
        while True:
            yield np.array([0.0, self.rd, 0.0])

    def _next_new_velocity_iterator(self, mu=0.0):
        while True:
            vx, vz = np.random.normal(mu, self.sigma, 2)
            vy = -self.mean_velocity * sqrt(-log(random.random()))
            yield np.array([vx, vy, vz])

    def set_initial_values(self, t0, X0):
        """
        Sets initial value to integrator

        Args:
            t0      initial time
            X0      list of initial values (x0, y0, z0, vx0, vy0, vz0)
        """

        self.solver.set_initial_value(X0, t0)

    def move_one(self, t1, N=1):
        """
        Move particle to time t1, using N subdivision of given time interval.

        Args:
            t1      time to move particle
            N       number of divisions from current time till t1

        Returns:
            bool    was solver successfull?
        """

        t = np.linspace(self.solver.t, t1, N+1)
        sol = np.empty((N+1, 6))
        sol[0] = self.solver.y
        # import pdb; pdb.set_trace()

        k = 1
        while self.solver.successful() and k < N+1:
            self.solver.integrate(t[k])
            sol[k] = self.solver.y
            k += 1

        return self.solver.successful(), sol[1:]

    def run(self):
        assert self.queue
        # x, y, z, vx, vy, vz, ncol
        data = np.zeros([self.npar, 7])
        tpar = 0
        ipar = 0

        while True:
            intersect, number_of_collisions = self.move_towards_domain(self.rdd, nsub=1000)
            tpar += 1
            if intersect:
                if ipar % self.show_progress_every_par == 0:
                    logger.info('iproc %s: catch particle no %s out of %s (tpar: %s)', self.iproc, ipar, self.npar, tpar)
                ipar += 1
                data[ipar-1, 0:6] = intersect
                data[ipar-1, 6] = number_of_collisions
                if ipar == self.npar:
                    logger.info('iproc %s: done; putting data into queue', self.iproc)
                    self.queue.put(data)
                    return

    def move_towards_domain(self, rdd, nsub=1000):

        collision_iter = self._next_coll_time()
        position_iter = self._next_new_position_iterator()
        velocity_iter = self._next_new_velocity_iterator()

        pos = next(position_iter)
        vel = next(velocity_iter)
        total_time = 0.0

        self.set_initial_values(total_time, np.array(list(pos) + list(vel)))
        x, y, z, vx, vy, vz = pos[0], pos[1], pos[2], vel[0], vel[1], vel[2]
        collision_number = 0

        # total_sol = list()

        while True:
            t = next(collision_iter)
            total_time += t
            succ, sol = self.move_one(total_time, 1)
            assert succ

            x0, y0, z0, vx0, vy0, vz0 = x, y, z, vx, vy, vz
            x, y, z, vx, vy, vz = sol[0]

            r = math.sqrt(x**2 + y**2 + z**2)
            # total_sol.append((total_time, x, y, z, vx, vy, vz))
            if r < rdd:
                # we return back to time total_time-t
                total_time = total_time - t
                x, y, z, vx, vy, vz = x0, y0, z0, vx0, vy0, vz0
                self.set_initial_values(total_time, np.array([x0, y0, z0, vx0, vy0, vz0]))
                dt = t / nsub
                for istep in xrange(int(nsub)):
                    # import pdb; pdb.set_trace()
                    total_time += dt
                    succ, sol = self.move_one(total_time, 1)
                    assert succ
                    x0, y0, z0, vx0, vy0, vz0 = x, y, z, vx, vy, vz
                    x, y, z, vx, vy, vz = sol[0]
                    r = math.sqrt(x**2 + y**2 + z**2)
                    if r < rdd:
                        # import pdb; pdb.set_trace()
                        r0 = math.sqrt(x0**2 + y0**2 + z0**2)
                        t_rdd = np.interp(rdd, [r, r0], [total_time-dt, total_time])
                        x_rdd = np.interp(t_rdd, [total_time-dt, total_time], [x0, x])
                        y_rdd = np.interp(t_rdd, [total_time-dt, total_time], [y0, y])
                        z_rdd = np.interp(t_rdd, [total_time-dt, total_time], [z0, z])
                        vx_rdd = np.interp(t_rdd, [total_time-dt, total_time], [vx0, vx])
                        vy_rdd = np.interp(t_rdd, [total_time-dt, total_time], [vy0, vy])
                        vz_rdd = np.interp(t_rdd, [total_time-dt, total_time], [vz0, vz])
                        # return True, total_sol, (x_rdd, y_rdd, z_rdd, vx_rdd, vy_rdd, vz_rdd)
                        return (x_rdd, y_rdd, z_rdd, vx_rdd, vy_rdd, vz_rdd), collision_number

                raise Exception('this really should not happed')

            if r > self.rd:
                # return False, total_sol, None
                return None, collision_number

            # generating velocity of neutral particle
            vxg = probe.mc.mc.mc.norm_rd(0.0, self.sigmag)
            vyg = probe.mc.mc.mc.norm_rd(0.0, self.sigmag)
            vzg = probe.mc.mc.mc.norm_rd(0.0, self.sigmag)

            if self.particle == 'el':
                # null collision technique
                velocity = math.sqrt((vx-vxg)**2 + (vy-vyg)**2 + (vz-vzg)**2)
                assert velocity < self.VmaxElectronCollision, '{} < {}'.format(velocity, self.VmaxElectronCollision)
                sigma_el_artificial = self.cross_const / velocity
                if random.random() < self.sigma_cs / sigma_el_artificial:
                    vx, vy, vz = probe.mc.mc.mc.collision(self.m, self.mg, vx, vy, vz, vxg, vyg, vzg)
                    self.set_initial_values(total_time, np.array([x, y, z, vx, vy, vz]))
                    collision_number += 1

            if self.particle == 'ari':
                vx, vy, vz = probe.mc.mc.mc.collision(self.m, self.mg, vx, vy, vz, vxg, vyg, vzg)
                self.set_initial_values(total_time, np.array([x, y, z, vx, vy, vz]))
                collision_number += 1

    def move_with_collisions(self, steps=10):

        assert steps is not None

        collision_iter = self._next_coll_time()
        position_iter = self._next_new_position_iterator()
        velocity_iter = self._next_new_velocity_iterator()

        pos = next(position_iter)
        vel = next(velocity_iter)
        total_time = 0.0

        self.set_initial_values(total_time, np.array(list(pos) + list(vel)))

        total_sol = np.empty((steps+1, 7))
        total_sol[0] = np.array([total_time, pos[0], pos[1], pos[2], vel[0], vel[1], vel[2]])

        for istep in xrange(steps):
            t = next(collision_iter)
            total_time += t
            succ, sol = self.move_one(total_time, 1)

            assert succ
            x, y, z, vx, vy, vz = sol[0]

            total_sol[istep+1] = np.array([total_time, x, y, z, vx, vy, vz])

            # generating velocity of neutral particle
            vxg = probe.mc.mc.mc.norm_rd(0.0, self.sigmag)
            vyg = probe.mc.mc.mc.norm_rd(0.0, self.sigmag)
            vzg = probe.mc.mc.mc.norm_rd(0.0, self.sigmag)

            if self.particle == 'el':
                # null collision technique
                velocity = math.sqrt((vx-vxg)**2 + (vy-vyg)**2 + (vz-vzg)**2)
                assert velocity < self.VmaxElectronCollision, '{} < {}'.format(velocity, self.VmaxElectronCollision)
                sigma_el_artificial = self.cross_const / velocity
                if random.random() < self.sigma_cs / sigma_el_artificial:
                    vx, vy, vz = probe.mc.mc.mc.collision(self.m, self.mg, vx, vy, vz, vxg, vyg, vzg)
                    self.set_initial_values(total_time, np.array([x, y, z, vx, vy, vz]))

            if self.particle == 'ari':
                vx, vy, vz = probe.mc.mc.mc.collision(self.m, self.mg, vx, vy, vz, vxg, vyg, vzg)
                self.set_initial_values(total_time, np.array([x, y, z, vx, vy, vz]))

        return total_sol

    @staticmethod
    def spher_analytic_er(t, X, q_o_m, C):
        """
        This function will be called by scipy's ode.

        Motion of particle in radial electric field. Electric potential is given by phi(r) = C/r^2,
        where C is constant from PIC simulation.

          dx/dt = vx
          dy/dt = vy
          dz/dt = vz
          dvx/dt = q/m*Ex
          dvy/dt = q/m*Ey
          dvz/dt = q/m*Ez

          Ex = Er*x/r
          Ey = Er*y/r
          Ez = Er*z/r

          r = sqrt(x^2 + y^2 + z^2)

          Er = 2*C/r^3

        Args:
            t       time (not relevant for this type of problem)
            X       is vector with variables to solve
            q_o_m   ratio of charge to mass of a given particle
            C       constants to compute Er
        """

        x, y, z, vx, vy, vz = X
        r = sqrt(x**2 + y**2 + z**2)
        const = 2 * q_o_m * C / r**4
        Y = [vx, vy, vz, const*x, const*y, const*z]
        return Y
