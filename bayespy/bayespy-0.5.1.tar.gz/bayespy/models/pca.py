# Copyright (c) 2016 Jaakko Luttinen
# MIT License

import numpy as np
import scipy
import bayespy as bp


def pca(data, n_components=2, noise='iso', mean='cols', features='cols'):

    (M, N) = np.shape(data)
    D = n_components

    X = bp.nodes.GaussianARD(0, 1, plates=(M, 1), shape=(D,), name='states')
    X_bias = bp.nodes.ConcatGaussian(X, [1])

    alpha = bp.nodes.Gamma(1e-8, 1e-8, plates=(D+1,), name='alpha')

    C_tau = bp.nodes.GaussianGamma(
        np.zeros(D+1),
        alpha.diag(),
        1e-5,
        1e-5,
        plates=(1, N),
        name='loadings'
    )

    F = bp.nodes.SumMultiply('i,i', X_bias, C_tau)

    Y = bp.nodes.GaussianARD(F, 1)

    alpha.initialize_from_value(1e-8)
    X.initialize_from_random()

    Q = bp.inference.VB(Y, F, C_tau, X, alpha)

    Y.observe(data, mask=~np.isnan(data))

    Q.update(repeat=2)

    Q.set_callback(lambda: rotate(X, C_tau, alpha, debug=False))

    Q.update(repeat=100)

    tau_C = C_tau.u[0]
    tau = C_tau.u[2]
    loadings = (tau_C / tau[...,None])[0,:,:]
    mean = loadings[:,-1]
    loadings = loadings[:,:-1]
    states = X.u[0][:,0,:]
    std = tau[0,:] ** (-0.5)

    return (loadings, states, mean, std)


    #return Q


def rotate(X, C_tau, alpha, debug=False):

    # print(F.get_moments()[0][:1,:1])
    # print(F.get_moments()[1][:1,:1])

    #
    # Find PCA rotation
    #

    D = X.dims[0][0]
    N = C_tau.plates[-1]

    # Move mean from X to bias loading
    mean_x = np.mean(X.get_moments()[0], axis=(-3, -2))
    bias_X = -mean_x
    c = C_tau.get_gaussian_location()
    mean_y = np.einsum('...i,...i', c[...,:-1], mean_x)
    bias_C = bp.utils.misc.concatenate(
        np.zeros((1,N,D)),
        mean_y[...,None],
        axis=-1
    )
    X.translate(bias_X, debug=debug)
    C_tau.translate(bias_C, debug=debug)

    # "Whiten" X
    xx = np.mean(X.get_moments()[1], axis=(-3, -4))
    L = np.linalg.cholesky(xx)
    logdet = np.sum(np.log(np.diag(L)))
    L_inv = scipy.linalg.solve_triangular(L, np.identity(D), lower=True)
    X.rotate(
        L_inv,
        inv=L,
        logdet=-logdet,
        debug=debug
    )
    C_tau.rotate(
        scipy.linalg.block_diag(L.T, [[1]]),
        inv=scipy.linalg.block_diag(L_inv.T, [[1]]),
        logdet=logdet,
        debug=debug
    )

    # Orthogonalize C and order the components
    cc_tau = np.mean(C_tau.get_moments()[1], axis=(-3, -4))
    (U, _, _) = np.linalg.svd(cc_tau[:-1,:-1])
    #print("DEBUG SVD", s)
    X.rotate(
        U.T,
        inv=U,
        logdet=0,
        debug=debug
    )
    C_tau.rotate(
        scipy.linalg.block_diag(U.T, [[1]]),
        inv=scipy.linalg.block_diag(U, [[1]]),
        logdet=0,
        debug=debug
    )

    # Update alpha (we assumed non-informative prior for it)
    alpha.update()

    # print(F.get_moments()[0][:1,:1])
    # print(F.get_moments()[1][:1,:1])

    return
