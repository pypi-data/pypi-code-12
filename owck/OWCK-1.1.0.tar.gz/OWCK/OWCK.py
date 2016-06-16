#OWCK class


import sys
from os import path

import numpy as np
from numpy import array, ones, inner, dot, diag, size
from numpy.random import shuffle
from copy import deepcopy

from sklearn.gaussian_process import GaussianProcess
from sklearn.gaussian_process import regression_models
from sklearn.tree import DecisionTreeRegressor
from mpi4py import MPI

from sklearn.cluster import KMeans
from sklearn.mixture import GMM
import skfuzzy as fuzz

from pandas import DataFrame


MACHINE_EPSILON = np.finfo(np.double).eps
class OWCK(GaussianProcess):
    """The Optimal Weighted Cluster Kriging/Gaussian Process class
    
    This class inherited from GaussianProcess class in sklearn library
    Most of the parameters are contained in sklearn.gaussian_process.
    
    Please check the docstring of Gaussian Process parameters in sklearn.
    Only newly introduced parameters are documented below.

    Parameters
    ----------
    n_cluster : int, optional
        The number of clusters, determines the number of the Gaussian Process
        model to build. It is the speed-up factor in OWCK.
    min_leaf_size : int, optional
        if min_leaf_size > 0, min_leaf_size is used to determine the number of clusters for
        the model tree clustering method.
    cluster_method : string, optional
        The clustering algorithm used to partition the data set.
        Built-in clustering algorithm are:
            'k-mean', 'GMM', 'fuzzy-c-mean', 'random', 'tree'
            Note that GMM, fuzzy-c-mean  are fuzzy clustering algorithms 
            With these algorithms you can set the overlap you desire.
            Tree is a non-fuzzy algorithm using local models per leaf in a regression tree
            The tree algorithm is also able to update the model with new records
    overlap : float, optional
        The percentage of overlap when using a fuzzy cluster method.
        Each cluster will be of the same size.
    is_parallel : boolean, optional
        A boolean switching parallel model fitting on. If it is True, then
        all the underlying Gaussian Process model will be fitted in parallel,
        supported by MPI. Otherwise, all the models will be fitted sequentially.
        
    Attributes
    ----------
    cluster_label : the cluster label of the training set after clustering
    clusterer : the clustering algorithm used.
    models : a list of (fitted) Gaussian Process models built on each cluster.
    
    References
    ----------
    
    .. [SWKBE15] `Bas van Stein, Hao Wang, Wojtek Kowalczyk, Thomas Baeck 
        and Michael Emmerich. Optimally Weighted Cluster Kriging for Big 
        Data Regression. In 14th International Symposium, IDA 2015, pages 
        310-321, 2015`
        http://link.springer.com/chapter/10.1007%2F978-3-319-24465-5_27#
    """

    def __init__(self, regr='constant', corr='squared_exponential', 
                 n_cluster=8, min_leaf_size=0, cluster_method='k-mean', overlap=0.0, beta0=None, 
                 storage_mode='full', verbose=False, theta0=0.1, thetaL=None, 
                 thetaU=None, optimizer='fmin_cobyla', random_start=1, 
                 normalize=True, nugget=10. * MACHINE_EPSILON, random_state=None, 
                 is_parallel=False):
        
        super(OWCK, self).__init__(regr=regr, corr=corr, 
                 beta0=beta0, storage_mode=storage_mode, verbose=verbose, 
                 theta0=theta0, thetaL=thetaL, thetaU=thetaU, 
                 optimizer=optimizer, random_start=random_start, 
                 normalize=normalize, nugget=nugget, 
                 random_state=random_state)
        
        self.n_cluster = n_cluster
        self.is_parallel = is_parallel
        self.verbose = verbose
        self.overlap = overlap #overlap for fuzzy clusters
        self.min_leaf_size = min_leaf_size
        
        if cluster_method not in ['k-mean', 'GMM', 'fuzzy-c-mean', 'random', 'tree']:
            raise Exception('{} clustering is not supported!'.format(cluster_method))
        else:
            self.cluster_method = cluster_method
            
    
    def __clustering(self, X, y=None):
        """
        The clustering procedure of the Optimal Weighted Clustering Gaussian 
        Process. This function should not be called externally
        """

        self.sizeX = len(X)
        
        if self.cluster_method == 'k-mean':
            clusterer = KMeans(n_clusters=self.n_cluster)
            clusterer.fit(X)
            self.cluster_label = clusterer.labels_
            self.clusterer = clusterer
        elif self.cluster_method == 'tree':
            
            if (self.min_leaf_size > 0):
                self.minsamples = min_leaf_size
                tree = DecisionTreeRegressor(random_state=0,min_samples_leaf=min_leaf_size)
            else:
                self.minsamples = int(len(X)/(self.n_cluster))
                tree = DecisionTreeRegressor(random_state=0,max_leaf_nodes=self.n_cluster)
            
            tree.fit(X,y)
            labels = tree.apply(X)
            clusters = np.unique(labels)
            k = len(clusters)
            if self.verbose:
                print ("leafs:",k)
            self.n_cluster = k
            self.leaf_labels = np.unique(labels)
            self.cluster_label = labels
            self.clusterer = tree
        elif self.cluster_method == 'random':
            r = self.n_sample % self.n_cluster
            m = (self.n_sample - r) / self.n_cluster
            self.cluster_label = array(range(self.n_cluster) * m + range(r))
            self.clusterer = None
            shuffle(self.cluster_label)
        elif self.cluster_method == 'GMM':    #GMM from sklearn
            self.clusterer = GMM(n_components=self.n_cluster, n_iter=1000)
            self.clusterer.fit(X)
            self.cluster_labels_proba = self.clusterer.predict_proba(X)
            self.cluster_label = self.clusterer.predict(X)
        elif self.cluster_method == 'fuzzy-c-mean': #Fuzzy C-means from sklearn
            cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(X.T, self.n_cluster, 2, error=0.000005, maxiter=10000, init=None)
            self.clusterer = cntr #save the centers for cmeans_predict
            self.cluster_labels_proba = u.T
            self.cluster_labels_proba = np.array(self.cluster_labels_proba)
            self.cluster_label = np.argmax(u, axis=0)
            self.cluster_label = np.array(self.cluster_label)
        
        
    def fit(self, X, y):
        """
        The Optimal Weighted Cluster Gaussian Process model fitting method.
        Parameters
        ----------
        X : double array_like
            An array with shape (n_samples, n_features) with the input at which
            observations were made.
        y : double array_like
            An array with shape (n_samples, ) or shape (n_samples, n_targets)
            with the observations of the output to be predicted.
        Returns
        -------
        ocwk : self
            A fitted Cluster Gaussian Process model object awaiting data to 
            perform predictions.
        """
        
        self.n_sample, self.n_feature = X.shape
        
        if y.shape[0] != self.n_sample:
            raise Exception('Training inuput and target do not match!')
        
        # clustering
        self.__clustering(X,y)
        
        # model creation
        if (self.cluster_method == 'tree'):
            self.models = [deepcopy(self) for i in self.leaf_labels]
        else:
            self.models = [deepcopy(self) for i in range(self.n_cluster)]
        
        for m in self.models:
            m.__class__ = GaussianProcess
        
        self.X = X
        self.y = y
        
        # model fitting
        if self.is_parallel:     # parallel model fitting
            
            # spawning processes...
            comm = MPI.COMM_SELF.Spawn(sys.executable, 
                                       args=[path.dirname(path.abspath(__file__)) + \
                                       '/OWCK_slave.py'],
                                       maxprocs=self.n_cluster)
            
            # prepare the training set for each GP model        
            if (self.cluster_method=='k-mean' or self.cluster_method=='random'):
                idx = [self.cluster_label == i for i in range(self.n_cluster)]
            elif (self.cluster_method=='tree'):
                idx = [self.cluster_label == self.leaf_labels[i] for i in range(self.n_cluster)]
            else:
                targetMemberSize = (len(self.X) / self.n_cluster)*(1.0+self.overlap)
                idx = []

                minindex = np.argmin(self.y)
                maxindex = np.argmax(self.y)
                for i in range(self.n_cluster):
                    idx_temp = np.argsort(self.cluster_labels_proba[:,i])[-targetMemberSize:]
                    if (minindex not in idx_temp):
                        idx_temp = np.hstack((idx_temp,[minindex]))
                    if (maxindex not in idx_temp):
                        idx_temp = np.hstack((idx_temp,[maxindex]))
                    idx.append(idx_temp)


            training_set = [(X[index, :], y[index]) for index in idx]
            
            # scatter the models and data
            comm.scatter(self.models, root=MPI.ROOT)
            comm.scatter([(k, training_set[k]) \
                for k in range(self.n_cluster)], root=MPI.ROOT)
            
            # Synchronization while the slave process are performing 
            # heavy computations...
            comm.Barrier()
                
            # Gether the fitted model from the childrenn process
            # Note that 'None' is only valid in master-slave working mode
            results = comm.gather(None, root=MPI.ROOT)
            
            # keep the fitted model align with their cluster
            fitted = DataFrame([[d['index'], d['model']] \
                for d in results], columns=['index', 'model'])
            fitted.sort('index', ascending=[True], inplace=True)
            
            self.models[:] = fitted['model']
                
            # free all slave processes
            comm.Disconnect()
        
        else:                    # sequential model fitting
            # get min and max value indexes such that no cluster gets 
            # only one value instances.
#            minindex = np.argmin(self.training_y)
#            maxindex = np.argmax(self.training_y)
            
            for i in range(self.n_cluster):                    
               
                if (self.cluster_method=='k-mean' or self.cluster_method=='random'):
                    idx = self.cluster_label == i
                elif (self.cluster_method=='tree'):
                    idx = self.cluster_label == self.leaf_labels[i]
                else:
                    targetMemberSize = (len(self.X) / self.n_cluster)*(1.0+self.overlap)
                    idx = []

                    minindex = np.argmin(self.y)
                    maxindex = np.argmax(self.y)

                    idx = np.argsort(self.cluster_labels_proba[:,i])[-targetMemberSize:]
                    if (minindex not in idx):
                        idx = np.hstack((idx,[minindex]))
                    if (maxindex not in idx):
                        idx = np.hstack((idx,[maxindex]))

                model = self.models[i]
                # TODO: discuss this will introduce overlapping samples
#                idx[minindex] = True
#                idx[maxindex] = True
                
                # dirty fix so that low nugget errors will increase the
                # nugget till the model fits
                while True:  
                    try:
                        # super is needed here to call the 'fit' function in the 
                        # parent class (GaussianProcess)
                        model.fit(self.X[idx, :], self.y[idx])
                        break
                    except ValueError:
                        if self.verbose:
                            print('Current nugget setting is too small!' +\
                                ' It will be tuned up automatically')
                        model.nugget *= 10
    
    def __mse_upper_bound(self, model):
        """
        This function computes the tight upper bound of the Mean Square Error(
        Kriging variance) for the underlying Posterior Gaussian Process model, 
        whose usage should be subject to Simple or Ordinary Kriging (constant trend)
        Parameters
        ----------
        model : a fitted Gaussian Process/Kriging model, in which 'self.regr'
                should be 'constant'
        Returns
        ----------
        upper_bound : the upper bound of the Mean Squared Error
        """
        
        if model.regr != regression_models.constant:
            raise Exception('MSE upper bound only exists for constant trend')
            
        C = model.C
        if C is None:
        # Light storage mode (need to recompute C, F, Ft and G)
            if model.verbose:
                print("This GaussianProcess used 'light' storage mode "
                          "at instantiation. Need to recompute "
                          "autocorrelation matrix...")
            _, par = model.reduced_likelihood_function()
            model.C = par['C']
            model.Ft = par['Ft']
            model.G = par['G']
    
        n_samples, n_features = model.X.shape
        tmp = 1 / model.G ** 2
    
        upper_bound = np.sum(model.sigma2 * (1 + tmp))
        return upper_bound

    
    def updateModel(self,newX, newY):
        """
        Add several instances to the data and rebuild models
        newX is a 2d array of (instances,features) and newY a vector
        """
        if (self.cluster_method=='tree'):

            #first update our data
            self.X = np.append(self.X, newX, axis=0)
            self.y = np.append(self.y, newY)

            #check the size of the new data
            if (len(self.X) > (self.sizeX + self.minsamples*2)):
                #in this case just rebuild all models
                #since number of models will change
                if self.verbose:
                    print("refitting all models")
                self.fit(self.X,self.y)
            else:
                rebuildmodels = np.unique(self.clusterer.apply(newX))
                rebuildmodelstemp = []
                for i in rebuildmodels:
                    rebuildmodelstemp.append(np.where(self.leaf_labels==i)[0][0])
                rebuildmodels = np.array(rebuildmodelstemp,dtype=int)
                labels = self.clusterer.apply(self.X)
                self.cluster_label = labels
                if self.is_parallel:     # parallel model fitting
                    # spawning processes...
                    if self.verbose:
                        print("Spawning new slaves to update models.")
                    comm = MPI.COMM_SELF.Spawn(sys.executable, 
                                               args=[path.dirname(path.abspath(__file__)) + \
                                               '/OWCK_slave.py'],
                                               maxprocs=len(rebuildmodels))
                    
                    idx = [self.cluster_label == self.leaf_labels[i] for i in rebuildmodels]
                    training_set = [(self.X[index, :], self.y[index]) for index in idx]
                    modelstosend = [self.models[i] for i in rebuildmodels]
                    # scatter the models and data
                    comm.scatter(modelstosend, root=MPI.ROOT)
                    comm.scatter([(k, training_set[k]) \
                        for k in range(len(rebuildmodels))], root=MPI.ROOT)
                    
                    # Synchronization while the slave process are performing 
                    # heavy computations...
                    comm.Barrier()
                        
                    # Gether the fitted model from the childrenn process
                    # Note that 'None' is only valid in master-slave working mode
                    results = comm.gather(None, root=MPI.ROOT)
                    
                    # keep the fitted model align with their cluster
                    fitted = DataFrame([[d['index'], d['model']] \
                        for d in results], columns=['index', 'model'])
                    fitted.sort('index', ascending=[True], inplace=True)
                    
                    for i in range(len(rebuildmodels)):
                        self.models[rebuildmodels[i]] = fitted['model'][i]
                        
                    # free all slave processes
                    comm.Disconnect()
                else:# is_parralel = false

                    for i in rebuildmodels:
                        if self.verbose:
                            print("updating model "+str(i)
                        idx = self.cluster_label == self.leaf_labels[i]
                        model = self.models[i]
                        while True:  
                            try:
                                # super is needed here to call the 'fit' function in the 
                                # parent class (GaussianProcess)
                                model.fit(self.X[idx, :], self.y[idx])
                                break
                            except ValueError:
                                if self.verbose:
                                    print('Current nugget setting is too small!' +\
                                        ' It will be tuned up automatically')
                                model.nugget *= 10
        else:
            #rebuild all models
            self.X = np.append(self.X, newX, axis=0)
            self.y = np.append(self.y, newY)
            self.fit(self.X,self.y)
    
    # TODO: implementating batch_size option to reduce the memory usage
    def predict(self, X, eval_MSE=True):
        """
        This function evaluates the Optimal Weighted Gaussian Process model at x.
        Parameters
        ----------
        X : array_like
            An array with shape (n_eval, n_features) giving the point(s) at
            which the prediction(s) should be made.
        eval_MSE : boolean, optional
            A boolean specifying whether the Mean Squared Error should be
            evaluated or not.
            Default assumes evalMSE = False and evaluates only the BLUP (mean
            prediction).
        batch_size : integer, Not available yet 
            An integer giving the maximum number of points that can be
            evaluated simultaneously (depending on the available memory).
            Default is None so that all given points are evaluated at the same
            time.
        Returns
        -------
        y : array_like, shape (n_samples, ) or (n_samples, n_targets)
            An array with shape (n_eval, ) if the Gaussian Process was trained
            on an array of shape (n_samples, ) or an array with shape
            (n_eval, n_targets) if the Gaussian Process was trained on an array
            of shape (n_samples, n_targets) with the Best Linear Unbiased
            Prediction at x.
        MSE : array_like, optional (if eval_MSE == True)
            An array with shape (n_eval, ) or (n_eval, n_targets) as with y,
            with the Mean Squared Error at x.
        """
        
        X = np.atleast_2d(X)
        X = X.T if size(X, 1) != self.n_feature else X
    
        n_eval, n_feature = X.shape
        
        if n_feature != self.n_feature:
            raise Exception('Dimensionality does not match!')
        
        if (self.cluster_method=='tree'):
            pred = []
            mse = []
            for x in X:
                modelindex = self.clusterer
                ix = self.clusterer.apply(x.reshape(1, -1))
                #print "ix",ix
                modelix = np.where(self.leaf_labels==ix)[0]
                
                if eval_MSE:
                    pred_x,mse_x = self.models[modelix[0]].predict(x.reshape(1, -1),eval_MSE=True)
                    pred.append(pred_x)
                    mse.append(mse_x)
                else:
                    pred_x = self.models[modelix[0]].predict(x.reshape(1, -1),eval_MSE=False)
                    pred.append(pred_x)
            if eval_MSE:
                return pred,mse
            else:
                return pred
        else: 
            # compute predictions and MSE from all underlying GP models
            # super is needed here to call the 'predict' function in the 
            # parent class
            res = array([model.predict(X, eval_MSE=True) \
                for model in self.models])
            
            # compute the upper bound of MSE from all underlying GP models
            mse_upper_bound = array([self.__mse_upper_bound(model) \
                for model in self.models])
                    
            if np.any(mse_upper_bound == 0):
                raise Exception('Something weird happened!')
                    
            pred, mse = res[:, 0, :], res[:, 1, :] 
            normalized_mse = mse / mse_upper_bound.reshape(-1, 1)
            
            # inverse of the MSE matrices
            Q_inv = [diag(1.0 / normalized_mse[:, i]) for i in range(n_eval)]
            
            _ones = ones(self.n_cluster)
            weight = lambda Q_inv: dot(_ones, Q_inv)
            normalizer = lambda Q_inv: dot(dot(_ones, Q_inv), _ones.reshape(-1, 1))
            
            # compute the weights of convex combination
            weights = array([weight(q_inv) / normalizer(q_inv) for q_inv in Q_inv])
            
            # make sure the weights sum to 1...  
            if np.any(abs(np.sum(weights, axis=1) - 1.0) > 1e-8):
                raise Exception('Computed weights do not sum to 1!')
            
            # convex combination of predictions from the underlying GP models
            pred_combined = array([inner(pred[:, i], weights[i, :]) \
                for i in range(n_eval)])
            
            # if overall MSE is needed        
            if eval_MSE:
                mse_combined = array([inner(mse[:, i], weights[i, :]**2) \
                    for i in range(n_eval)])
            
                return pred_combined, mse_combined
            
            else:
                return pred_combined
    	

	
	
	
