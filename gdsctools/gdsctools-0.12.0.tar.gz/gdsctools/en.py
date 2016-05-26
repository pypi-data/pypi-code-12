from sklearn import linear_model
import numpy as np

def en1(X, y):

    X_train = X[0:600]
    X_test = X[600:]
    y_train = y[0:600]
    y_test = y[600:]

    # Compute train and test errors
    alphas = np.logspace(-5, 1, 60)
    enet = linear_model.ElasticNet(l1_ratio=0.7)
    train_errors = list()
    test_errors = list()
    for alpha in alphas:
        enet.set_params(alpha=alpha)
        enet.fit(X_train, y_train)
        train_errors.append(enet.score(X_train, y_train))
        test_errors.append(enet.score(X_test, y_test))
        
    i_alpha_optim = np.argmax(test_errors)
    alpha_optim = alphas[i_alpha_optim]
    print("Optimal regularization parameter : %s" % alpha_optim)

    # Estimate the coef_ on full data with optimal regularization parameter
    enet.set_params(alpha=alpha_optim)
    coef_ = enet.fit(X, y).coef_

    ###############################################################################
    # Plot results functions

    import matplotlib.pyplot as plt
    plt.subplot(2, 1, 1)
    plt.semilogx(alphas, train_errors, label='Train')
    plt.semilogx(alphas, test_errors, label='Test')
    plt.vlines(alpha_optim, plt.ylim()[0], np.max(test_errors), color='k',
           linewidth=3, label='Optimum on test')
    plt.legend(loc='lower left')
    plt.ylim([0, 1.2])
    plt.xlabel('Regularization parameter')
    plt.ylabel('Performance')




    # Show estimated coef_ vs true coef
    plt.subplot(2, 1, 2)
    plt.plot(train_errors)
    #plt.plot(coef, label='True coef')
    #plt.plot(coef_, label='Estimated coef')
    #plt.legend()
    #plt.subplots_adjust(0.09, 0.04, 0.94, 0.94, 0.26, 0.26)
    #plt.show()

    return train_errors, test_errors



def en2(X, y, l1_ratio=0.7):

    from sklearn import cross_validation
    N = len(y)

    k_fold = cross_validation.KFold(n=N, n_folds=10, shuffle=True)

    # indices
    #for train_indices, test_indices in k_fold:
    #     print('Train: %s | test: %s' % (train_indices, test_indices))


    enet = linear_model.ElasticNet(l1_ratio=l1_ratio)
    # can be used for fitting:
    scores = [enet.fit(X[train], y[train]).score(X[test],y[test])  for train, test in k_fold]


    # To compute the score method of an estimator, the sklearn exposes a helper function:   
    #cross_validation.cross_val_score(svc, X_digits, y_digits, cv=kfold, n_jobs=-1)
    #array([ 0.93489149,  0.95659432,  0.93989983])
    return scores


def tune_l1_ratio(X, y):
    from matplotlib import errorbar
    alpha = np.logspace(-5,1,60)
    res = [en.en2(X, Y, l1_ratio=this) for this in alpha]
    res = np.array(res)
    errorbar(alphas, res.mean(axis=1), res.std(axis=1))

    # This may be more efficient:
    lm = linear_model.ElasticNetCV()
    lm.fit(X, y)
    f.alpha_



"""def en3(X, y):
    enet = linear_model.ElasticNet(l1_ratio=l1_ratio)
    k_fold = cross_validation.KFold(n=N, n_folds=10, shuffle=True)
    scores = [enet.fit(X[train], y[train]).score(X[test],y[test])  for train, test in k_fold]
    return scores
"""
