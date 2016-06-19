import pandas as pd
import numpy as np
from statistics import mode

class manudataclean:
    '''
    H.1) Human assisted Data Cleaning; identify invalid values and/or rows,
    create a list of possible actions that could be taken and create an user interface for a human to decide what to do
    - NAN, missing, outliers, unreliable values, out of the range.
    Once the action is chosen, perform the action.

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

        dev_num_manual = self.traindata.select_dtypes(include=numerics)
        dev_nonnum_manual = self.traindata.select_dtypes(exclude=numerics)

        if self.testdata is not None:
            val_num_manual = self.testdata.select_dtypes(include=numerics)
            val_nonnum_manual = self.testdata.select_dtypes(exclude=numerics)

        colnames_num_manual = list(dev_num_manual.columns.values)
        colnames_nonnum_manual = list(dev_nonnum_manual.columns.values)

        for names in idtargetlist:
            if names in colnames_num_manual:
                colnames_num_manual.remove(names)
            if names in colnames_nonnum_manual:
                colnames_nonnum_manual.remove(names)

        print("Processing non-numeric variables")

        for column in colnames_nonnum_manual:
            print("Processing variable ", column)
            colmode = mode(dev_nonnum_manual.loc[:, column])
            dev_nonnum_manual.loc[:, column].to_replace(to_replace="", value=colmode)
            allvalues = np.unique(dev_nonnum_manual.loc[:, column])
            if val_filename != "NA":
                val_nonnum_manual.loc[:, column].to_replace(to_replace="", value=colmode)
                for row in val_nonnum_manual.loc[:, column]:
                    if row not in allvalues:
                        row = colmode
            print("Variable ", column, "is clean")

        print("Processing numeric variables")

        for column in colnames_num_manual:
            print("Processing variable ", column)
            colmeanorig = np.mean(dev_num_manual.loc[:, column])
            colstdev = np.std(dev_num_manual.loc[:, column])
            temp = dev_num_manual.loc[:, column].tolist()
            for i in temp:
                if np.abs((i - colmeanorig)) > 3 * colstdev:
                    temp.remove(i)
            colmean = np.mean(temp)
            colmedian = np.median(temp)
            colmin = np.min(temp)
            colmax = np.max(temp)
            na_unreliable_replacement = int(input(
                "Choose NA and unreliable value replacement method : 1.Mean 2.Median 3.Specific user-input value, by entering the corresponding number : "))
            if na_unreliable_replacement == 1:
                dev_num_manual.loc[:, column].fillna(colmean)
            elif na_unreliable_replacement == 2:
                dev_num_manual.loc[:, column].fillna(colmedian)
            else:
                na_unreliable_replacement_value = input("Enter the value to replace NAs and unreliable values with : ")
                dev_num_manual.loc[:, column].fillna(na_unreliable_replacement_value)
            outlier_outofrange_replacement = int(input(
                "Choose outlier and out of range value replacement method : 1.Mean 2.Median 3. Minimum or maximum value based on value 4.Specific user-input value, by entering the corresponding number : "))
            if outlier_outofrange_replacement not in (1, 2, 3):
                outlier_outofrange_replacement_value_lower = input(
                    "Enter the value to replace lower end outliers and out of range values with : ")
                outlier_outofrange_replacement_value_higher = input(
                    "Enter the value to replace higher end outliers and out of range values with : ")
            for row in dev_num_manual.loc[:, column]:
                if float(row) < colmeanorig - 3 * colstdev:
                    if outlier_outofrange_replacement == 1:
                        row = colmean
                    elif outlier_outofrange_replacement == 2:
                        row = colmedian
                    elif outlier_outofrange_replacement == 3:
                        row = colmin
                    else:
                        row = outlier_outofrange_replacement_value_lower
                if float(row) > colmeanorig + 3 * colstdev:
                    if outlier_outofrange_replacement == 1:
                        row = colmean
                    elif outlier_outofrange_replacement == 2:
                        row = colmedian
                    elif outlier_outofrange_replacement == 3:
                        row = colmax
                    else:
                        row = outlier_outofrange_replacement_value_higher
            if self.testdata is not None:
                if na_unreliable_replacement == 1:
                    val_num_manual.loc[:, column].fillna(colmean)
                elif na_unreliable_replacement == 2:
                    val_num_manual.loc[:, column].fillna(colmedian)
                else:
                    val_num_manual.loc[:, column].fillna(na_unreliable_replacement_value)
                for row in val_num_manual.loc[:, column]:
                    if float(row) < colmin or float(row) < colmeanorig - 3 * colstdev:
                        if outlier_outofrange_replacement == 1:
                            row = colmean
                        elif outlier_outofrange_replacement == 2:
                            row = colmedian
                        elif outlier_outofrange_replacement == 3:
                            row = colmin
                        else:
                            row = outlier_outofrange_replacement_value_lower
                    if float(row) > colmax or float(row) > colmeanorig + 3 * colstdev:
                        if outlier_outofrange_replacement == 1:
                            row = colmean
                        elif outlier_outofrange_replacement == 2:
                            row = colmedian
                        elif outlier_outofrange_replacement == 3:
                            row = colmax
                        else:
                            row = outlier_outofrange_replacement_value_higher
            print("Variable ", column, "is clean\n\n")

        print("Manual cleaning is complete")
        print("Cleaned numeric variables are available in dev_num_manual and val_num_manual")
        print("Cleaned non-numeric variables are available in dev_nonnum_manual and val_nonnum_manual")

# dev = pd.read_csv("dev.csv")
# oot = pd.read_csv("oot0.csv")
# A = manudataclean(dev,oot)
