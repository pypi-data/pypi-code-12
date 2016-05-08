    def _sign_residuals(self, p, obj, channel):
        print('_sign_residuals')
        err = self._leastsq_residuals(p, obj, channel)
        return np.sign(err) * np.median(np.abs(err))

    def sign_fit(self, obj, inplace=False):
        '''
        Fit a dataset to a reference dataset by applying an offset to
        find the least-squared error. Uses scipy.optimize.leastsq()

        obj: reference object, of instance Data.
        
        inplace: if True modify self, otherwise modify a copy.

        Returns self (or a copy if 'inplace' is False) with an
        adjustment applied for best fit.
        '''

        # See http://www.tau.ac.il/~kineret/amit/scipy_tutorial/ for
        # helpful tutorial on using leastsq().
        import scipy.optimize

        for c in self.channels:
            assert c in obj.channels, 'Channel not in reference object'

        err_func = self._sign_residuals
        # err_func = self._leastsq_residuals
        
        if inplace:
            r = self
        else:
            r = copy.deepcopy(self)

        # Fit each channel separately
        for c in self.channels:
            channel = self.channels[0]
            p0 = [0.0]
            plsq = scipy.optimize.leastsq(err_func, p0, 
                                      args=(obj, channel))
            print(plsq)
            r.data[self.get_channel_index(c)] -= plsq[0]

        return r
