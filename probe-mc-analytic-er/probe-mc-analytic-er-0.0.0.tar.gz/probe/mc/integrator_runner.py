import logging
import multiprocessing
import h5py

from .integrator import Integrator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.propagate = False


def run_integrator_in_parallel(nproc, ndata, **kwargs):

    queue = multiprocessing.Queue(nproc)

    kwargs['queue'] = queue
    integrators = list()

    for iproc in xrange(nproc):
        kwargs['iproc'] = iproc
        integrators.append(Integrator(**kwargs))

    for iproc, integrator in enumerate(integrators):
        logger.info('running integrator no %s', iproc)
        integrator.start()

    f = h5py.File('data.h5', 'w')

    idata = 0
    while True:
        data = queue.get()
        logger.info('got data %s from queue', idata)
        logger.debug('got data: %s', data)
        dset = f.create_dataset('data_{:05d}'.format(idata), (kwargs['npar'], 7))
        dset[...] = data

        idata += 1
        if idata == ndata-1:
            for integrator in integrators:
                integrator.terminate()
            break

        for iproc, integrator in enumerate(integrators):
            if not integrator.is_alive():
                logger.info('proc %s is not alive; replacing', iproc)

        kwargs['iproc'] = iproc
        integrators[iproc] = Integrator(**kwargs)
        integrators[iproc].start()