#!/usr/bin/env python

# Part of the psychopy_ext library
# Copyright 2016 Jonas Kubilius
# The program is distributed under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.

"""
A very rudimentary and experimental wrapper around mturkutils for running
experiments on Amazon Mechanical Turk.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import glob, datetime, argparse, shutil
import cPickle as pickle
from warnings import warn

import numpy as np
import scipy
import pandas

import pymongo
import mturkutils


class Experiment(mturkutils.base.Experiment):

    def __init__(self, single=False, short=False, save=True, *args, **kwargs):
        self.single = single
        self.short = short
        self.save = save
        super(Experiment, self).__init__(*args, **kwargs)
        if self.sandbox:
            print('**WORKING IN SANDBOX MODE**')
        delattr(self, 'meta')

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except:
            if name in ['meta','exp_plan']:
                value = getattr(self, 'get_' + name)()
                setattr(self, name, value)
                return self.__dict__[name]
            else:
                raise

    def createTrials(self):
        d = self.exp_plan

        self._trials = {
            'isi1': d['isi1'].tolist(),
            'stim': self.get_obj_url(),
            'stim_dur': d['stim_dur'].tolist(),
            'gap_dur': d['gap_dur'].tolist(),
            'mask': self.get_mask_url(),
            'mask_dur': d['mask_dur'].tolist(),
            'isi2': d['isi2'].tolist(),
            'label1': self.get_label_url('label1'),
            'label2': self.get_label_url('label2')
        }

    def get_exp_plan(self):
        fnames = sorted(glob.glob(self.bucket + '_exp_plan_*.pkl'))[::-1]

        if len(fnames) == 0:
            print('Creating exp_plan')
            exp_plan = self.create_exp_plan()
        else:
            if len(fnames) > 0:
                print('exp_plan files found:')
                for i, fname in enumerate(fnames):
                    print(i+1, fname, sep=' - ')
                print(0, 'Create a new exp_plan', sep=' - ')
                choice = raw_input('Choose which one to load (default is 1): ')

                if choice == '0':
                    print('Creating exp_plan')
                    self.create_exp_plan()
                    fname = sorted(glob.glob(self.bucket + '_exp_plan_*.pkl'))[-1]
                else:
                    if choice == '': choice = '1'
                    try:
                        fname = fnames[int(choice)-1]
                    except:
                        raise
            else:
                fname = fnames[0]

            print('Using', fname, end='\n\n')
            exp_plan = pickle.load(open(fname))
            # exp_plan = exp_plan.addcols(np.repeat([1], len(meta)).astype(int), names=['batch'])

        if self.single:
            exp_plan = exp_plan[:self.trials_per_hit]
        elif self.short:
            exp_plan = exp_plan[:10]
            
        return exp_plan

    def save_exp_plan(self, exp_plan):
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
        fname = '_'.join([self.bucket_name, 'exp_plan', date]) + '.pkl'
        pickle.dump(exp_plan, open(fname, 'wb'))
        print('Saved exp_plan to:', fname)

    def get_hitids(self):
        prefix = 'sandbox' if self.sandbox else 'production'
        pattern = self.bucket + '_' + prefix + '_hitids_*.pkl'
        fnames = sorted(glob.glob(pattern))[::-1]

        if len(fnames) == 0:
            raise Exception('No HIT ID files found with pattern ' + pattern)
        elif len(fnames) > 1:
            print('HIT ID files found:')
            for i, fname in enumerate(fnames):
                print(i+1, fname, sep=' - ')
            choice = raw_input('Choose which one to load (default is 1): ')

            if choice == '': choice = '1'
            try:
                fname = fnames[int(choice)-1]
            except:
                raise
        else:
            fname = fnames[0]

        print('Using', fname, end='\n\n')
        hitids = pickle.load(open(fname))
        return hitids

    def check_hits(self):
        return self.check_if_hits_are_completed()

    def check_if_hits_are_completed(self):
        """
        Checks if all HITs have been completed.

        Prints the answer and also return True or False.
        """
        results = mturkutils.base.download_results(self.get_hitids(), sandbox=self.sandbox)
        completed = [len(assign) > 0 for assign, hit in results]
        print('{} out of {} HITs completed'.format(sum(completed), len(completed)))
        return completed

    def download_results(self, hitids=None):
        if hitids is None: hitids = self.get_hitids()
        idx = 0
        for subjid, hitid in enumerate(hitids):
            subj_data = self.getHITdata(hitid, full=False)
            assert len(subj_data) == 1  # don't know what to do otherwise

            for subj in subj_data:
                assert isinstance(subj, dict)

                data = zip(subj['ImgOrder'], subj['Response'], subj['RT'])
                for k, (img, resp, rt) in enumerate(data):
                    imgid = mturkutils.base.getidfromURL(img[0])
                    assert imgid == self.exp_plan['id'][idx]
                    # respid = mturkutils.base.getidfromURL(resp)
                    # respid = respid[:-len(self.label_prefix)]
                    self.exp_plan['subj_resp'][idx] = self.exp_plan['label' + str(resp+1)][idx]
                    self.exp_plan['acc'][idx] = int(self.exp_plan['corr_resp'][idx] == self.exp_plan['subj_resp'][idx])
                    self.exp_plan['rt'][idx] = rt
                    idx += 1

    # def get_workedids(self)

    def updateDBwithHITs(self, verbose=False, overwrite=False):
        hitids = self.get_hitids()
        self.download_results(hitids)
        coll = self.collection
        idx = 0
        for subjid, hitid in enumerate(hitids):
            subj_data = self.getHITdata(hitid, full=False)
            coll.ensure_index([
                ('WorkerID', pymongo.ASCENDING),
                ('Timestamp', pymongo.ASCENDING)],
                unique=True)

            assert len(subj_data) == 1  # don't know what to do otherwise

            for subj in subj_data:
                assert isinstance(subj, dict)

                try:
                    doc_id = coll.insert(subj, safe=True)
                except pymongo.errors.DuplicateKeyError:
                    if not overwrite:
                        warn('Entry already exists, moving to next...')
                        continue
                    if 'WorkerID' not in subj or 'Timestamp' not in subj:
                        warn("No WorkerID or Timestamp in the subject's "
                                "record: invalid HIT data?")
                        continue
                    spec = {'WorkerID': subj['WorkerID'],
                            'Timestamp': subj['Timestamp']}
                    doc = coll.find_one(spec)
                    assert doc is not None
                    doc_id = doc['_id']
                    if '_id' in subj:
                        _id = subj.pop('_id')
                        if verbose and str(_id) not in str(doc_id) \
                                and str(doc_id) not in str(_id):
                            print('Dangling _id:', _id)
                    coll.update({'_id': doc_id}, {
                        '$set': subj
                        }, w=0)

                if verbose:
                    print('Added:', doc_id)

                # handle ImgData
                m = self.exp_plan[self.exp_plan['subjid'] == subjid]
                m = pandas.DataFrame(m).to_dict('records')
                coll.update({'_id': doc_id}, {'$set': {'ImgData': m}}, w=0)



# class Timing(object):
#
#     def __init__(self, save=True):
#         self.save = save
#         self.bucket = 'hvm10-var6-timing-nogap'

def fit_psy(self, df, f, x='stim_dur', y='acc', hue=['obj', 'imgno'],
            ci=95, n_boot=1000
            ):

    f = lambda x,a,b,c: c * np.arctan((x - a) / b) / np.pi

    # gr = df_new_f.groupby(['obj', 'imgno', 'id', 'distractor']).groups.keys()
    # gr = {(g[0], g[1]): (g[2], g[3]) for g in gr}
    #
    # agg = stats.aggregate(df_new_f, groupby=groupby, reset_index=False)[values].unstack('imgno')
    # count = stats.aggregate(df_new_f, groupby=groupby, reset_index=False, aggfunc=len)[values]

def _fit_psy(self, df, f, x='stim_dur', y='acc', hue=['obj', 'imgno']):

    b = lambda x: np.mean(np.random.choice(x, size=len(x), replace=True))
    agg = df.pivot_table(index=hue, columns=index, values=values, aggfunc=b)
    p = lambda x: pandas.Series(scipy.optimize.curve_fit(f, x.index, x.values)[0])
    params = agg.apply(p, axis=1)
    return params

def _fit_psy_dprime(df, f, iterno, bootstrap=True, save=True,
                    x='stim_dur', y='acc',
                    hue=['obj', 'distractor', 'imgno'],
                    target='obj', distractor='distractor'):

    if isinstance(x, (str, unicode)): x = [x]
    if isinstance(hue, (str, unicode)): hue = [hue]
    dfb = df.copy()
    np.random.seed(iterno)

    if bootstrap:
        b = lambda x: np.random.choice(x, size=len(x), replace=True)
        dfb[y] = dfb.groupby(x+hue)[y].transform(b)

    hits = dfb.groupby(hue + x)[y].mean()

    distr = dfb.groupby([distractor, target] + x)[y].mean()
    fas_f = lambda x: distr[(x.name[1], x.name[0], x.name[2])]
    fas_tmp = 1 - hits.reset_index().groupby([target, distractor] + x).acc.transform(fas_f)
    fas = hits.copy()
    fas[:] = fas_tmp.values

    dprime = hits.apply(scipy.stats.norm.ppf) - fas.apply(scipy.stats.norm.ppf)
    dprime = dprime.reset_index()
    dprime.rename(columns={y: "d'"}, inplace=True)
    dprime.loc[dprime["d'"]>5, "d'"] = 5
    dprime.loc[dprime["d'"]<-5, "d'"] = -5

    agg = dprime.groupby(hue+x)["d'"].mean().unstack(x)
    def curve_fit(x):
        try:
            pars = scipy.optimize.curve_fit(f, x.index, x.values)[0]
        except:
            pars = (np.nan, np.nan, np.nan)
        return pandas.Series(pars)
    params = agg.apply(curve_fit, axis=1)
    if save:
        params.to_pickle('computed/est_boot_{:0>3d}.pkl'.format(iterno))
    return params


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('task')
    parser.add_argument('func')
    parser.add_argument('-p', '--production', action='store_true')
    parser.add_argument('--single', action='store_true')
    parser.add_argument('--short', action='store_true')
    parser.add_argument('-n', '--dry', action='store_true')
    args, extras = parser.parse_known_args()
    kwargs = {}
    for kwarg in extras:
        k, v = kwarg.split('=')
        kwargs[k.strip('-')] = v
    print()

    return args, kwargs

def run_exp(exp=None, dataset=None):
    args, kwargs = get_args()

    if args.task == 'dataset':
        if dataset is None:
            raise Exception('Please provide Dataset')
        getattr(dataset(), args.func)(**kwargs)

    elif args.task == 'exp':
        if exp is None:
            raise Exception('Please provide Dataset')
        exp = exp(sandbox=not args.production, single=args.single,
                  short=args.short, save=not args.dry)
        if args.func == 'create':
            exp.create_exp_plan()
        elif args.func == 'prep':
            exp.createTrials()
            shutil.rmtree(exp.tmpdir)
            exp.prepHTMLs()
        elif args.func == 'upload':
            exp.createTrials()
            shutil.rmtree(exp.tmpdir)
            exp.prepHTMLs()
            exp.testHTMLs()
            exp.uploadHTMLs()
        elif args.func == 'create_hits':
            exp.createTrials()
            shutil.rmtree(exp.tmpdir)
            exp.prepHTMLs()
            exp.testHTMLs()
            exp.uploadHTMLs()
            exp.createHIT(secure=True)
        elif args.func == 'download':
            exp.download_results(**kwargs)
            import pdb; pdb.set_trace()
        elif args.func == 'download_and_store':
            exp.updateDBwithHITs(**kwargs)
        elif args.func == 'test_data':
            data = exp.download_results()
            import pdb; pdb.set_trace()
            return data
        else:
            getattr(exp, args.func)(**kwargs)

    else:
        eval(args.func)(**kwargs)
