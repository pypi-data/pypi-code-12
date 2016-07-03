# /usr/bin/env python
# -*- encoding: utf-8 -*-

# Simulation of Multi-armed Bandits

import sys, math, json
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import truncnorm
import random as rndm
import collections
# matplotlib.use('TkAgg')
# plt.rcParams["figure.figsize"] = (6, 4)


# ## Class: Arm

# In[188]:

# Constants
INF = 10**5
PRESET_RESULTS = INF
FILE_OUTPUT = False


# In[189]:

class Arm():
    def __init__(self, distribution='nd', label=None, mean=None, sd=None):
        self.dist = distribution
        self.mean = self.sigma = None
        while self.mean is None or self.mean > 1.0 or self.mean < .0:
            self.mean = mean or np.random.normal(.5, .1, 1)[0]
        while self.sigma is None or self.sigma > 1.0 or self.sigma < .0:
#             self.sigma = sd or np.random.normal(.1, .1, 1)[0]
            self.sigma = 0.25
        self.label = label
        self.results = [ e for e in np.random.normal(self.mean, self.sigma, PRESET_RESULTS) if e >= 0.0 and e <= 1.0 ]
#         self.results = [ v+self.mean for v in truncnorm.rvs(-self.mean, 1.0-self.mean, scale=1.0, size=PRESET_RESULTS) ]
        self.pointer = 0

    def pick(self):
        if self.pointer >= PRESET_RESULTS: raise ValueError("No more results.")
        reward = self.results[self.pointer]
        while reward < 0.0 or reward > 1.0:
            self.pointer += 1
            reward = self.results[self.pointer]
#         if reward > 1.0: reward = 1.0
#         if reward < 0.0: reward = 0.0
#         self.pointer += 1
        return reward



# ## Class: MAB

# In[190]:

class MAB():
#     def __init__(self, arms, distribution='nd'):
#         self.k = arms
#         self.dist = distribution
#         self.arms = [Arm(distribution=self.dist) for _ in range(0, self.k)]
#         if FILE_OUTPUT:
#             with open("./preset_results.csv", 'a') as f:
#                 for j in range(0, 500):
#                     values = [str(self.arms[i].results[j]) for i in range(0, len(self.arms))]
#                     record = ",".join(values)
#                     f.write(record + "\n")

    def __init__(self, arms, distribution='nd'):
        self.arms = arms
        self.dist = distribution
        self.arms = [Arm(distribution=self.dist, label=a['label'] or None, mean=a['mean'] or None, sd=a['sd'] or None) for a in self.arms]
        if FILE_OUTPUT:
            with open("./preset_results.csv", 'a') as f:
                for j in range(0, 500):
                    values = [str(self.arms[i].results[j]) for i in range(0, len(self.arms))]
                    record = ",".join(values)
                    f.write(record + "\n")

    def pick(self, i):
        # Pick ith arm
        reward = self.arms[i].pick()
        for arm in self.arms:
            arm.pointer += 1
        return reward

    def draw_arms_histogram(self, i=None):
        if i:
            x = self.arms[i].results
            plt.hist(x)
            plt.figure()
        else:
            for arm in self.arms:
                x = arm.results
                plt.hist(x)
                plt.figure()

    def combinations(self, limit=None):
        # Compute number of combinations with less than L arms among K arms
        # arguments
        # * limit: Limitation of the number of arms that consist a super-arm
        # * draw: Option to draw graph
        # * table: Option to show table

        if limit and type(limit)!=int: return "L should be int or None."

        combs = {}
        f = math.factorial
        combs = {i:f(self.k)/f(i)/f(self.k-i) for i in range(1, self.k+1)}

        if limit and type(limit)==int:
            if limit > self.k: return "L should be smaller than or equal to K."
            if limit < 0: return 0
            combsum = 0
            for k,v in combs.iteritems():
                if k <= limit: combsum += v
            return combsum
        else:
            return combs

    def draw_combinations(self):
        # Draw number of combinations for each possible number of arms
        x = np.linspace(1, self.k, self.k, endpoint=True)
        y = [self.combinations(i) for i in range(1, self.k+1)]
        plt.xlabel('Number of incentives')
        plt.ylabel('Nuber of combinations')
        plt.plot(x,y)
#         plt.figure()
#         plt.draw()
        plt.savefig('combinations.png', format='png', dpi=960)
        plt.show()
#         plt.close()
        return None


# ## Class: MAB_Algorithm

# In[191]:

class MAB_Algorithm(object):
    def __init__(self, mab):
        self.name = 'MAB Algorithm'
        self.mab = mab
        for arm in self.mab.arms:
            arm.pointer = 0
        ranking = [8, 1, 3, 2, 5, 6, 7, 9, 4] # 実際の利得の順位
        # 期待利得の初期値を0で始める場合
        self.status = { i:{ "estimated_mean": .0, "total_reward": .0, "stddev": .0, "results": [] } for i in range(0, len(self.mab.arms)) }
        # 期待利得の初期値を1で始める場合
#         self.status = { i:{ "estimated_mean": 1.0, "total_reward": .0, "stddev": .0, "results": [] } for i in range(0, len(self.mab.arms)) }
        # 期待利得分布の初期値に，実際の利得分布と同じ値を与える場合
#         self.status = { i:{ "estimated_mean": self.mab.arms[i].mean, "total_reward": .0, "stddev": .0, "results": [] } for i in range(0, len(self.mab.arms)) }
        # 期待利得分布の初期値に，実際の利得分布と異なる値で平均値の順序のみを保存したランダム値を与える場合
#         self.status = { i:{ "estimated_mean": np.random.normal(0.75 - 0.05*ranking[i], .1, 1)[0], "total_reward": .0, "stddev": .0, "results": [] } for i in range(0, len(self.mab.arms)) }
        # 期待利得分布の初期値に，実際の利得分布と異なる値で平均値の順序のみを保存したランダム値(平均値の分散が小さい)を与える場合
#         self.status = { i:{ "estimated_mean": np.random.normal(0.6 - 0.01*ranking[i], .1, 1)[0], "total_reward": .0, "stddev": .0, "results": [] } for i in range(0, len(self.mab.arms)) }
        # 期待利得分布の初期値に，実際の利得分布と異なる値で平均値の上位半分，下位半分のみ保存したランダム値を与える場合
        # 期待利得分布の初期値に，ランダム値を与える場合
#         self.status = { i:{ "estimated_mean": np.random.normal(0.5, .1, 1)[0], "total_reward": .0, "stddev": .0, "results": [] } for i in range(0, len(self.mab.arms)) }

        self.played_rounds = 0

    def make_decision(self):
        return None

    def play(self):
        arm = self.make_decision()
        reward = self.mab.pick(arm)
        if FILE_OUTPUT:
            with open("./%s.csv" % self.name, 'a') as f:
                f.write("%s,%s,%s\n" % (self.mab.arms[arm].pointer, arm, reward))
        return { "arm": arm, "reward": reward }

    def simulate(self, rounds):
        self.rounds = rounds
        for r in range(0, rounds):
            self.played_rounds = r
            # Play this round
            result = self.play()
            arm = result["arm"]
            reward = result["reward"]

            # Update results
            self.status[arm]["results"].append({r: reward})

            # Update other statuses
            total = .0
            for v in self.status[arm]["results"]:
                total += float(v.values()[0])
            self.status[arm]["total_reward"] = float(total)
            self.status[arm]["estimated_mean"] = float(total)/float(len(self.status[arm]["results"]))
            var = .0
            for v in self.status[arm]["results"]:
                var += (self.status[arm]["estimated_mean"] - float(v.values()[0]))**2
            self.status[arm]["stddev"] = math.sqrt(var/float(len(self.status[arm]["results"])))

    def result(self):
        result = {}
        result["total_reward"] = sum([v["total_reward"] for k, v in self.status.iteritems()])
        result["status"] = self.status
        return result

    def show_result(self):
        print "Arm\tTotal Reward\tEstimated Mean\tTrue Mean\tPlayed Rounds"
        for k, v in self.status.iteritems():
            print "%s\t%s\t%s\t%s\t%s" % (k, v["total_reward"], v["estimated_mean"], self.mab.arms[k].mean, len(v["results"]))
        print "Total Reward = %s" % self.result()["total_reward"]

    def graph_result(self):
        estimated_means = [v["estimated_mean"] for k, v in self.status.iteritems()]
        std_estimated_mean = [v["stddev"] for k, v in self.status.iteritems()]
        true_means = [m.mean for m in self.mab.arms]

        fig, ax = plt.subplots()
        index = np.arange(len(self.mab.arms))
        bar_width = 0.4
        alpha = 0.5

        rects1 = plt.bar(index, estimated_means, bar_width, color='b', alpha=alpha, yerr=std_estimated_mean, label="Estimated Mean")
        rects2 = plt.bar(index + bar_width, true_means, bar_width, color='r', alpha=alpha, label="True Mean")

        plt.xlabel('Arm')
        plt.ylabel('Reward')
        plt.title('Mean reward of each arm')
        plt.xticks(index + bar_width, [str(k) for k, v in self.status.iteritems()])
        plt.legend()

#         plt.tight_layout()
        plt.show()


# In[192]:

# Oracle(Always picks the best arm at each time)
class Oracle(MAB_Algorithm):
    def __init__(self, mab):
        super(Oracle, self).__init__(mab)
        self.name = 'oracle'
    def true_best_arm(self):
        max_mean = -INF
        selection = None
        for k, v in self.status.iteritems():
            arm = self.mab.arms[k]
            if arm.results[arm.pointer] > max_mean:
                selection = k
                max_mean = arm.results[arm.pointer]
        return selection

    def make_decision(self):
        return self.true_best_arm()



# In[193]:

# Random Algorithm
class Random(MAB_Algorithm):
    def __init__(self, mab):
        super(Random, self).__init__(mab)
        self.name = 'random'
    def make_decision(self):
        return np.random.choice(len(self.mab.arms), 1)[0]


# In[194]:

# Epsilon First Algorithm
class Epsilon_First(MAB_Algorithm):
    def __init__(self, mab, epsilon=.5):
        super(Epsilon_First, self).__init__(mab)
        self.name = 'epsilon_first'
        self.epsilon = epsilon

    def best_arm(self):
        max_mean = -INF
        selection = None
        for k,v in self.status.iteritems():
            if v["estimated_mean"] > max_mean:
                selection = k
                max_mean = v["estimated_mean"]
        return selection

    def make_decision(self):
        if float(self.played_rounds) < float(self.rounds)*self.epsilon:
            return np.random.choice(len(self.mab.arms), 1)[0]
        else:
            return self.best_arm()


# In[195]:

# Epsilon-Greedy Algorithm
class Epsilon_Greedy(MAB_Algorithm):
    def __init__(self, mab, epsilon=.12):
        super(Epsilon_Greedy, self).__init__(mab)
        self.name = 'epsilon_greedy'
        self.epsilon = epsilon

#     def best_arm(self):
#         max_eval = float(-INF)
#         for k, v in self.status.iteritems():
#             evaluation = v["estimated_mean"]
#             if evaluation > max_eval:
#                 max_eval = evaluation
#                 selection = k
#         return k

    def best_arm(self):
        max_mean = -INF
        selection = None
        for k,v in self.status.iteritems():
            if v["estimated_mean"] > max_mean:
                selection = k
                max_mean = v["estimated_mean"]
        return selection

    def make_decision(self):
#         for i in range(0, len(self.mab.arms)):
#             if len(self.status[i]["results"]) == 0:
#                 return i
        best = self.best_arm()
        others = []
        for k, v in self.status.iteritems():
            if k==best:
                v["probability"] = 1.0 - self.epsilon + self.epsilon/float(len(self.mab.arms))
            else:
                others.append(k)
                v["probability"] = self.epsilon/float(len(self.mab.arms))

        r = rndm.random()
        if r <= self.status[best]['probability']:
            selection = best
        else:
            selection = others[int((r - self.status[best]['probability'])/(self.epsilon/float(len(self.mab.arms))))]
        return selection


# In[196]:

# Boltzmann Exploration (Softmax)
class Softmax(MAB_Algorithm):
    def __init__(self, mab, tau=.5):
        super(Softmax, self).__init__(mab)
        self.name = 'softmax'
        self.tau = float(tau)

    def make_decision(self):
        for i in range(0, len(self.mab.arms)):
            if len(self.status[i]["results"]) == 0:
                return i

        divider = sum([ math.exp(v["estimated_mean"]/self.tau) for k, v in self.status.iteritems() ])

        for k, v in self.status.iteritems():
            v["probability"] = math.exp(v["estimated_mean"]/self.tau)/divider

        r = rndm.random()
        selection = None
        for k, v in self.status.iteritems():
            r -= v["probability"]
            if r <= 0.0:
                selection = k
                break
        return selection


# In[197]:

# Pursuit Algorithms


# In[198]:

# Reinforcement Comparison


# In[199]:

# UCB Algorithm
class UCB(MAB_Algorithm):
    def __init__(self, mab):
        super(UCB, self).__init__(mab)
        self.name = 'ucb'

    def make_decision(self):
        for i in range(0, len(self.mab.arms)):
            if len(self.status[i]["results"]) == 0:
                return i
        max_eval = float(-INF)
        selection = None
        for k, v in self.status.iteritems():
            evaluation = v["estimated_mean"] + math.sqrt(float(2.0*math.log(float(self.played_rounds)))/float(len(v["results"])))
            if evaluation > max_eval:
                max_eval = evaluation
                selection = k
        return selection


# In[200]:

# Single Incentive
class Single_Incentive(MAB_Algorithm):
    def __init__(self, mab, label):
        super(Single_Incentive, self).__init__(mab)
        self.name = label
    def make_decision(self):
        for idx, arm in enumerate(self.mab.arms):
            if arm.label == self.name:
                return idx


# ## Simulation
#
# Algorithms: From "Algorithms for the multi-armed bandit problem"

# ### Initialization

# In[201]:

# K = 13 # アーム数
T = 1000 # ラウンド数
# mab = MAB(K)

# 予備実験に基づくシミュレーション
incentives = []

# Q3
incentives.append({ "label": "Bayesian Truth Serum", "mean": 0.300, "sd": None })
incentives.append({ "label": "Punishment Accuracy", "mean": 0.737, "sd": None })
incentives.append({ "label": "Reward Accuracy", "mean": 0.487, "sd": None })
incentives.append({ "label": "Trust", "mean": 0.507, "sd": None })
incentives.append({ "label": "Humanization", "mean": 0.414, "sd": None })
incentives.append({ "label": "Solidarity", "mean": 0.400, "sd": None })
incentives.append({ "label": "Cheap Talk - Normative", "mean": 0.350, "sd": None })
incentives.append({ "label": "Cheap Talk - Survaillance", "mean": 0.233, "sd": None })
incentives.append({ "label": "Tournament Scoring", "mean": 0.425, "sd": None })

# Q4
# incentives.append({ "label": "Bayesian Truth Serum", "mean": 0.520, "sd": None })
# incentives.append({ "label": "Punishment Accuracy", "mean": 0.743, "sd": None })
# incentives.append({ "label": "Reward Accuracy", "mean": 0.487, "sd": None })
# incentives.append({ "label": "Trust", "mean": 0.750, "sd": None })
# incentives.append({ "label": "Humanization", "mean": 0.575, "sd": None })
# incentives.append({ "label": "Solidarity", "mean": 0.555, "sd": None })
# incentives.append({ "label": "Cheap Talk - Normative", "mean": 0.500, "sd": None })
# incentives.append({ "label": "Cheap Talk - Survaillance", "mean": 0.600, "sd": None })
# incentives.append({ "label": "Tournament Scoring", "mean": 0.520, "sd": None })

trials = [ MAB(incentives) for _ in range(0, 10) ]
results_simulation = [ {} for _ in range(0, 10) ]


# In[202]:

# 初期状態の妥当性チェック
# mab.draw_arms_histogram()


# In[203]:

# Oracle
for idx, mab in enumerate(trials):
    oracle = Oracle(mab)
    oracle.simulate(T)
    oracle.show_result()
    oracle.graph_result()
    results_simulation[idx]['Oracle'] = oracle.result()['total_reward']


# In[204]:

# Random
for idx, mab in enumerate(trials):
    random = Random(mab)
    random.simulate(T)
    random.show_result()
    random.graph_result()
    results_simulation[idx]['Random'] = random.result()['total_reward']
# results_simulation[''] = []
# for mab in trials:
#     results_simulation[''].append(oracle.result()['total_reward'])


# In[205]:

# Epsilon First

label_ef = []
# result_ef = []
for idx, mab in enumerate(trials):
    EPSILON = .04
    for i in range(1, 14):
        label = "Epsilon First(e=%s)" % (EPSILON*float(i)*20.0)
        if label not in label_ef: label_ef.append(label)
        epsilon_first = Epsilon_First(mab, EPSILON*float(i)*20.0)
        epsilon_first.simulate(T)
        epsilon_first.show_result()
        epsilon_first.graph_result()
        results_simulation[idx][label] = epsilon_first.result()['total_reward']

#     label_ef.append("Epsilon First(e=%s)" % (EPSILON*float(i)))
#     result_ef.append(epsilon_first.result()["total_reward"])

# results_simulation[''] = []
# for mab in trials:
#     results_simulation[''].append(oracle.result()['total_reward'])


# In[206]:

# Epsilon Greedy
# EPSILON = 0.5
# epsilon_greedy = Epsilon_Greedy(mab, EPSILON)
# epsilon_greedy.simulate(T)
# epsilon_greedy.show_result()
# epsilon_greedy.graph_result()


label_eg = []
result_eg = []
for idx, mab in enumerate(trials):
    EPSILON = .06
    for i in range(1, 14):
        label = "Epsilon Greedy(e=%s)" % (EPSILON*float(i)*20.0)
        if label not in label_eg: label_eg.append(label)
        epsilon_greedy = Epsilon_Greedy(mab, EPSILON*float(i)*20.0)
        epsilon_greedy.simulate(T)
        epsilon_greedy.show_result()
        epsilon_greedy.graph_result()
        results_simulation[idx][label] = epsilon_greedy.result()['total_reward']
#         label_eg.append("Epsilon Greedy(e=%s)" % (EPSILON*float(i)))
#         result_eg.append(epsilon_greedy.result()["total_reward"])


# In[207]:

# Boltzmann Exploration (Softmax)
label_sm = []
for idx, mab in enumerate(trials):
    TAU = .04
    for i in range(1, 14):
        label = "Softmax(t=%s)" % (TAU*float(i)*20.0)
        if label not in label_sm: label_sm.append(label)
        softmax = Softmax(mab, TAU*float(i)*20.0)
        softmax.simulate(T)
        softmax.show_result()
        softmax.graph_result()
        results_simulation[idx][label] = softmax.result()['total_reward']
#         label_sm.append("Softmax(t=%s)" % (TAU*float(i)))
#         result_sm.append(softmax.result()["total_reward"])


# In[208]:

# UCB
for idx, mab in enumerate(trials):
    ucb = UCB(mab)
    ucb.simulate(T)
    ucb.show_result()
    ucb.graph_result()
    results_simulation[idx]["UCB"] = ucb.result()['total_reward']


# In[209]:

# Single Incentives
label_si = []
for idx, mab in enumerate(trials):
    for incentive in incentives:
        label = "Single(%s)" % incentive['label']
        if label not in label_si: label_si.append(label)
        single = Single_Incentive(mab, label=incentive['label'])
        single.simulate(T)
        single.show_result()
        single.graph_result()
        results_simulation[idx][label] = single.result()['total_reward']


# ### 複数回(K=9, T=1000, 100回繰り返しで平均値)

# In[210]:

# print results_simulation
with open('./simulation/output/result.json', 'w') as f:
    f.write(json.dumps(results_simulation, indent=2))
    f.write('\n')

plt.rcParams["figure.figsize"] = (12, 20)
srs = [ collections.OrderedDict(sorted(r.items())) for r in results_simulation ]  # sorted results_simulation

x = ["Oracle", "Random"] + label_si + label_ef + label_eg + label_sm + ["UCB"]
summary = {}
for incentive in x:
    sum_reward = sum([ res[incentive] for res in srs ])
    mean_reward = sum_reward/float(len(srs))
    sum_sq = sum([ (mean_reward-res[incentive])**2.0 for res in srs ])
    sd = math.sqrt(sum_sq)/float(len(srs))
    summary[incentive] = {'mean':mean_reward, 'sd':sd}

with open('./simulation/output/summary.json', 'w') as f:
    f.write(json.dumps(summary, indent=2))
    f.write('\n')

y = [ summary[incentive]['mean'] for incentive in x ]
yerr = [ summary[incentive]['sd'] for incentive in x ]
index = np.arange(len(x))

bar_width = 0.7
alpha = 0.5

fig, ax = plt.subplots()
for i, v in enumerate(y):
    ax.text(v + 10, i + .1, round(v, 1), color='black')

# plt.rcParams["figure.figsize"] = (12, 10)
barlist = plt.barh(index, y, bar_width, xerr=yerr, alpha=alpha, label="Total Reward")
for idx, bar in enumerate(barlist):
    if x[idx].find("Oracle") >= 0: bar.set_color('r')
    elif x[idx].find("Random") >= 0: bar.set_color('r')
    elif x[idx].find("Single") >= 0: bar.set_color('g')
    elif x[idx].find("Epsilon First") >= 0: bar.set_color('b')
    elif x[idx].find("Epsilon Greedy") >= 0: bar.set_color('g')
    elif x[idx].find("Softmax") >= 0: bar.set_color('b')
    elif x[idx].find("UCB") >= 0: bar.set_color('g')
barlist[0].set_color('r')
plt.ylabel('Algorithm')
plt.xlabel('Total Reward')
plt.title('Total reward of each algorithm')
plt.yticks(index+bar_width/2.0, x)

fig_size = plt.rcParams["figure.figsize"]

plt.figure()
plt.show()


# ### グラフが大きすぎるので分割

# In[211]:

# print results_simulation
# with open('./simulation/output/result.json', 'w') as f:
#     f.write(json.dumps(results_simulation, indent=2))
#     f.write('\n')

# with open('./simulation/output/summary.json', 'w') as f:
#     f.write(json.dumps(summary, indent=2))
#     f.write('\n')

# アウトプットしたファイルからJSON読み込み
with open('./simulation/output/summary.json', 'r') as f:
    summary = json.loads(f.read())
# print(summary)

plt.rcParams["figure.figsize"] = (8, 6)
srs = [ collections.OrderedDict(sorted(r.items())) for r in results_simulation ]  # sorted results_simulation

x = ["Oracle", "Random"] + label_si + ["Epsilon First(e=0.04)", "Epsilon Greedy(e=0.06)", "Softmax(t=0.04)", "UCB"]
# xs = []
# xs.append(["Oracle", "Random"] + label_si)
# xs.append(["Oracle", "Random"] + ["Epsilon First(e=0.04)"])
# xs.append(["Oracle", "Random"] + ["Epsilon Greedy(e=0.12)"])
# xs.append(["Oracle", "Random"] + ["Softmax(e=0.04)"])
# xs.append(["Oracle", "Random"] + ["UCB"])

# for x in xs:
y = [ summary[incentive]['mean'] for incentive in x ]
yerr = [ summary[incentive]['sd'] for incentive in x ]
index = np.arange(len(x))

bar_width = 0.7
alpha = 0.5

fig, ax = plt.subplots()
for i, v in enumerate(y):
    ax.text(v + 10, i + .1, round(v, 1), color='black')

# plt.rcParams["figure.figsize"] = (12, 10)
barlist = plt.barh(index, y, bar_width, color='g', xerr=yerr, alpha=alpha, label="Total Reward")
for idx, bar in enumerate(barlist):
    if x[idx].find("Oracle") >= 0: bar.set_color('r')
    elif x[idx].find("Random") >= 0: bar.set_color('r')
    elif x[idx].find("Single") >= 0: bar.set_color('g')
    else: bar.set_color('b')
barlist[0].set_color('r')
plt.ylabel('Algorithm')
plt.xlabel('Total Reward')
plt.title('Total reward of each algorithm')
plt.yticks(index+bar_width/2.0, x)
plt.tight_layout()

fig_size = plt.rcParams["figure.figsize"]

plt.savefig('./simulation/output/simulation_selected.png', format='png', dpi=500)
plt.figure()
# plt.show()


# ### 各アルゴリズムの合計利得

# In[ ]:

# # FIXED: OracleよりEpsilon Firstのほうが良い場合があるので直す
# # x = ["Oracle", "Random", "Epsilon First(e=0.1)", "Epsilon Greedy(e=0.1)", "UCB"]
# x = ["Oracle", "Random"] + label_ef + label_eg + label_sm + ["UCB"]
# index = np.arange(len(x))
# # y = [oracle.result()["total_reward"], random.result()["total_reward"], epsilon_first.result()["total_reward"], epsilon_greedy.result()["total_reward"], ucb.result()["total_reward"]]
# y = [oracle.result()["total_reward"], random.result()["total_reward"]] + result_ef + result_eg + result_sm + [ucb.result()["total_reward"]]

# bar_width = 0.7
# alpha = 0.5

# fig, ax = plt.subplots()
# for i, v in enumerate(y):
#     ax.text(v + 3, i + .1, round(v, 1), color='black')
# #     ax.text(v + 3, i + .25, str(v), color='blue', fontweight='bold')

# plt.rcParams["figure.figsize"] = (12, 30)
# barlist = plt.barh(index, y, bar_width, alpha=alpha, label="Total Reward")
# # barlist = plt.barh(index, y, bar_width, color='b', alpha=alpha, label="Total Reward")
# for idx, bar in enumerate(barlist):
#     if x[idx].find("Oracle") >= 0: bar.set_color('r')
#     elif x[idx].find("Random") >= 0: bar.set_color('r')
#     elif x[idx].find("Epsilon First") >= 0: bar.set_color('b')
#     elif x[idx].find("Epsilon Greedy") >= 0: bar.set_color('g')
#     elif x[idx].find("Softmax") >= 0: bar.set_color('b')
#     elif x[idx].find("UCB") >= 0: bar.set_color('g')
# barlist[0].set_color('r')
# plt.ylabel('Algorithm')
# plt.xlabel('Total Reward')
# plt.title('Total reward of each algorithm')
# plt.yticks(index+bar_width/2.0, x)

# fig_size = plt.rcParams["figure.figsize"]
# print "Current size:", fig_size

# # Set figure width to 12 and height to 9
# # fig_size[0] = 12
# # fig_size[1] = 9

# plt.figure()
# plt.show()


# ### 組み合わせ数
#
# $\Sigma^{K}_{i=1} {}_KC_i$

# In[ ]:

# K = 13
# L = 13

# mab = MAB(K)

# print mab.combinations(limit=L)
# mab.draw_combinations()


# In[ ]:
