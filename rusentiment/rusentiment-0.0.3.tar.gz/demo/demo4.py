# -*- coding: utf-8 -*-
import pickle

import pandas

import numpy
from pip._vendor.distlib.compat import raw_input
from sklearn.cross_validation import train_test_split
from sklearn.metrics import precision_recall_fscore_support
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier



#raw_data = pandas.read_csv('/Users/sergeysmetanin/PycharmProjects/graduation_work/src/sentiment/data/kinopoisk_custom.csv',
#                           names=['?', 'id','meta', 'text', 'label'], error_bad_lines=False, sep='\t')
from sentiment import SentimentClassifier

raw_data = pandas.read_csv('/Users/sergeysmetanin/PycharmProjects/graduation_work/src/sentiment/data/kinopoisk.csv',
                           names=['text', 'label'], error_bad_lines=False)
data = list(raw_data['text'].values)
labels = [l == 'POS' for l in raw_data['label'].values]


#labels = raw_data['label'].values[:700]
#labels = [v=='True' for v in labels]

#print len(data)
#print len(set(data))




# clf = SentimentClassifier(maltp_working_dir="/Users/sergeysmetanin/UntitledFolder4/maltparser-1.8.1")
# clf.fit(data, labels)

# with open('clf.pkl', 'wb') as f:
#     pickle.dump(clf, f, pickle.HIGHEST_PROTOCOL)



for sy in [True]:
    for p in [True]:
        for st in [True]:
            r = []
            for i in xrange(20):
                X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=i)
                clf = SentimentClassifier(maltp_working_dir="/Users/sergeysmetanin/UntitledFolder4/maltparser-1.8.1", ngram_range=(1, 2), syntax=sy,
                                          preprocessing=p, stemming=st)
                clf.fit(X_train, y_train)
                # print clf.score(X_test, y_test)
                prf = precision_recall_fscore_support(y_test, clf.predict_list(X_test), average='macro')
                r.append(prf)
                #print prf
            r = numpy.array(r)
            f = open('results_nb(1,2).txt', 'a')
            print sy, p, st, numpy.mean(r[:, 0]), numpy.mean(r[:, 1]), numpy.mean(r[:, 2])
            f.write(str([sy, p, st]))
            f.write(': ')
            f.write(str([numpy.mean(r[:, 0]), numpy.mean(r[:, 1]), numpy.mean(r[:, 2])]))
            f.write('\n')
            f.close()
