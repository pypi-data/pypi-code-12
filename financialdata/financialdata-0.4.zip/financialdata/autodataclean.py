import pandas as pd
import numpy as np
from statistics import mode

class autodataclean:
    '''
    A.1) Automated Data Cleaning; identify invalid values and/or rows and automatically solve the problem-
    NAN, missing, outliers, unreliable values, out of the range, automated data input.
    (Your group decide a solution for the each problem!)

    Reference - http://pandas.pydata.org/pandas-docs/stable/missing_data.html

    Process -

    1. Check type of column - numeric/non-numeric
    2. For non-numeric -
        a. Replace missing and out of range by most common (mode) in dev
    3. For numeric -
        a. Compute dev mean, median, min and max excluding outliers and unreliable values
        b. For automated -
            i. Replace NA and unreliable by mean of dev
            ii. Replace outliers and out of range by min or max of dev as applicable
        c. For human assisted -
            i. For NAs and unreliable values, give option of replacing by mean, median or user input value
            ii. For outliers and out of range values, give option of replacing by mean, median, min, max or user input

    Note - Replacement values are always computed on dev and replacements in val are always same as dev treatment

    Note - Exclude ID and target from cleaning process

    Note - case 1 : one file, like MBD_FA2; case 2 : multiple files, one dev and others val, test, oot etc.
    '''

    def __init__(self, traindata, testdata = None):
        '''Constructor for this class'''
        self.traindata = pd.DataFrame(traindata)
        if testdata is not None:
            self.testdata = pd.DataFrame(testdata)
        else:
            self.testdata = None
        self.main()

    def main(self):
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        idtargetlist = ['id', 'ob_target', 'ID', 'TARGET']

        dev_num_auto = self.traindata.select_dtypes(include=numerics)
        dev_nonnum_auto = self.traindata.select_dtypes(exclude=numerics)

        if self.testdata is not None:
            val_num_auto = self.testdata.select_dtypes(include=numerics)
            val_nonnum_auto = self.testdata.select_dtypes(exclude=numerics)

        colnames_num_auto = list(dev_num_auto.columns.values)
        colnames_nonnum_auto = list(dev_nonnum_auto.columns.values)

        for names in idtargetlist:
            if names in colnames_num_auto:
                colnames_num_auto.remove(names)
            if names in colnames_nonnum_auto:
                colnames_nonnum_auto.remove(names)

        print("Processing non-numeric variables")

        for column in colnames_nonnum_auto:
            print("Processing variable ", column)
            colmode = mode(dev_nonnum_auto.loc[:, column])
            dev_nonnum_auto.loc[:, column].to_replace(to_replace="", value=colmode)
            allvalues = np.unique(dev_nonnum_auto.loc[:, column])
            if val_filename != "NA":
                val_nonnum_auto.loc[:, column].to_replace(to_replace="", value=colmode)
                for row in val_nonnum_auto.loc[:, column]:
                    if row not in allvalues:
                        row = colmode
            print("Variable ", column, "is clean")

        print("Processing numeric variables")

        for column in colnames_num_auto:
            print("Processing variable ", column)
            colmeanorig = np.mean(dev_num_auto.loc[:, column])
            colstdev = np.std(dev_num_auto.loc[:, column])
            temp = dev_num_auto.loc[:, column].tolist()
            for i in temp:
                if np.abs((i - colmeanorig)) > 3 * colstdev:
                    temp.remove(i)
            colmean = np.mean(temp)
            colmedian = np.median(temp)
            colmin = np.min(temp)
            colmax = np.max(temp)
            dev_num_auto.loc[:, column].fillna(colmean)
            for row in dev_num_auto.loc[:, column]:
                if row < colmeanorig - 3 * colstdev:
                    row = colmin
                if row > colmeanorig + 3 * colstdev:
                    row = colmax
            if self.testdata is not None:
                val_num_auto.loc[:, column].fillna(colmean)
                for row in val_num_auto.loc[:, column]:
                    if row < colmin or row < colmeanorig - 3 * colstdev:
                        row = colmin
                    if row > colmax or row > colmeanorig + 3 * colstdev:
                        row = colmax
            print("Variable ", column, "is clean")
        print("Automated cleaning is complete")
        print("Cleaned numeric variables are available in dev_num_auto and val_num_auto")
        print("Cleaned non-numeric variables are available in dev_nonnum_auto and val_nonnum_auto")

# dev = pd.read_csv("dev.csv")
# oot = pd.read_csv("oot0.csv")
# A = autodataclean(dev,oot)
