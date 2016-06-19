import pandas as pd
import numpy as np
import operator
from scipy.stats import entropy

def check_best_bin(data, variable, target, potential_bins):
    """
    Returns the best bin among the list of potential bins.
    :param data:
    :param variable:
    :param target:
    :param potential_bins:
    :return:
    """
    entropies = {}
    for bin in potential_bins:
        newdata = data.copy(deep=True)
        newbin = create_bins(data, variable, [bin])
        newdata['newbin'] = pd.Series(newbin, index=data.index)
        freqtable = pd.crosstab(index=newdata["newbin"], columns=newdata[target])
        # print(freqtable)

        if (len(freqtable.columns) == 2) and (len(freqtable) == 2):
            firstbinsum = freqtable.ix[0, 0] + freqtable.ix[0, 1]
            secondbinsum = freqtable.ix[1, 0] + freqtable.ix[1, 1]
            total = freqtable.ix[0, 0] + freqtable.ix[0, 1] + freqtable.ix[1, 0] + freqtable.ix[1, 1]
            bin_entropy = (firstbinsum / total) * entropy(freqtable.ix[0], base=2) + (secondbinsum / total) * entropy(
                freqtable.ix[1], base=2)
        else:
            bin_entropy = 1

        entropies[bin] = bin_entropy
    best_bin = min(entropies.items(), key=operator.itemgetter(1))[0]
    if entropies[best_bin] == 1:
        best_bin = None
    return best_bin

def create_bins(data, variable, bins):
    """
    Creates bins for a dataset.
    :param data:
    :param variable:
    :param bins:
    :return:
    """
    newbin = []
    length = len(bins)
    value = np.array(data[variable])
    for i in range(0, len(data)):
        if value[i] <= bins[0]:
            newbin.append("<= "+str(bins[0]))
        for j in range(length-1):
            if value[i] > bins[j] and value[i] <= bins[j+1]:
                newbin.append(str(bins[j])+" - "+str(bins[j+1]))
        if value[i] > bins[length-1]:
            newbin.append("> "+str(bins[length-1]))
    return newbin

class autobindummy:

    def __init__(self, traindata, testdata, target):
        '''Constructor for this class'''
        self.traindata = pd.DataFrame(traindata)
        self.testdata = pd.DataFrame(testdata)
        self.target = target
        self.nbins = 0
        self.main()

    def main(self):

        data_float = self.traindata.select_dtypes(include=[np.float])
        data_int = self.traindata.select_dtypes(include=[np.int64])
        varlist = list(data_float.columns)


        if any(x in self.target for x in varlist):
            varlist.remove(self.target)
        print(varlist)

        varlist_cat = list(data_int.columns)
        if any(x in self.target for x in varlist_cat):
            varlist_cat.remove(self.target)

        varlist_cat_copy = varlist_cat.copy()

        for var in varlist_cat_copy:
            uniquevalues = self.traindata[var].unique()
            length_unique = len(uniquevalues)
            # print(var+' '+str(length_unique))
            ratio = length_unique/len(self.traindata)
            if (ratio > 0.01) or (length_unique <= 2):
                varlist_cat.remove(var)
        print(varlist_cat)

        # targetvalues = self.traindata[self.target].unique()
        # freqtable = pd.value_counts(self.traindata[self.target].values, sort=False)
        # target_freqprob = []
        # target_freqprob.append(freqtable[targetvalues[0]]/(freqtable[targetvalues[0]]+freqtable[targetvalues[1]]))
        # target_freqprob.append(freqtable[targetvalues[1]]/(freqtable[targetvalues[0]]+freqtable[targetvalues[1]]))
        # target_entropy = entropy(target_freqprob, base=2)
        # my_bins = np.linspace(min, max, self.nbins-1)

        if len(self.traindata) > 1000:
            self.nbins = 4
        else:
            self.nbins = 2

        for k in range(2):
            bins = []
            max = np.max(self.traindata[varlist[k]])
            min = np.min(self.traindata[varlist[k]])
            mid = int((max-min)/2)
            quarter = int(mid/2)
            potential_bins = [quarter, mid, quarter+mid]
            bestbin = check_best_bin(self.traindata, varlist[k], self.target, potential_bins)
            bins.append(bestbin)

            while len(bins) <= (self.nbins):

                length = len(bins)
                # print("\nLENGTH "+str(length)+" NO OF BINS "+str(self.nbins))
                for j in range(length+1):
                    if j == 0:
                        min = np.min(self.traindata[varlist[k]])
                        # print("Lower Min " + str(min))
                        max = bins[j]
                        # print("Lower Max " + str(max))
                        mid = int((max - min) / 2)
                        quarter = int(mid / 2)
                        potential_bins = [quarter, mid, quarter+mid]
                        newdata = self.traindata[self.traindata[varlist[k]] <= max]
                        bestbin = check_best_bin(newdata, varlist[k], self.target, potential_bins)

                    elif j == length:
                        min = bins[j-1]
                        # print("Upper Min "+str(min))
                        max = np.max(self.traindata[varlist[k]])
                        # print("Upper Max " + str(max))
                        mid = int((max - min) / 2)
                        quarter = int(mid / 2)
                        potential_bins = [min+quarter, min+mid, min+quarter+mid]
                        newdata = self.traindata[self.traindata[varlist[k]] > min]
                        bestbin = check_best_bin(newdata, varlist[k], self.target, potential_bins)

                    else:
                        min = bins[j-1]
                        # print("Middle Min "+str(min))
                        max = bins[j]
                        # print("Middle Max "+str(max))
                        mid = int((max - min) / 2)
                        quarter = int(mid / 2)
                        potential_bins = [min + quarter, min + mid, min + quarter + mid]
                        newdata = self.traindata[(self.traindata[varlist[k]] > min) & (self.traindata[varlist[k]] <= max)]
                        bestbin = check_best_bin(newdata, varlist[k], self.target, potential_bins)

                    if bestbin is not None:
                        bins.append(bestbin)
                bins.sort()

            print("Final Bins")
            print(bins)

            # Create Final Bins
            newbin = create_bins(self.traindata, varlist[k], bins)
            self.traindata[str(varlist[k])+'_bin'] = pd.Series(newbin, index=self.traindata.index)
            newbin_test = create_bins(self.testdata, varlist[k], bins)
            self.testdata[str(varlist[k])+'_bin'] = pd.Series(newbin_test, index=self.testdata.index)

            # Dummy Creation
            newbindummies = pd.get_dummies(newbin)
            self.traindata = pd.concat([self.traindata, newbindummies],axis = 1)
            newbindummies_test = pd.get_dummies(newbin_test)
            self.testdata = pd.concat([self.testdata, newbindummies_test],axis = 1)

            # Create Bins for Categorical Variables
            # newbindummiescat = pd.get_dummies(varlist_cat[0])
            # self.traindata = pd.concat([self.traindata, newbindummiescat], axis = 1)
            # newbindummiescat_test = pd.get_dummies(varlist_cat[0])
            # self.testdata = pd.concat([self.testdata, newbindummiescat_test], axis=1)


        print(self.traindata)
        print(self.testdata)

dev = pd.read_csv("dev.csv")
oot = pd.read_csv("oot0.csv")
A = autobindummy(dev,oot,'ob_target')




