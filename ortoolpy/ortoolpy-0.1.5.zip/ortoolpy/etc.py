# coding: utf-8
"""
Copyright: 2015 Saito Tsutomu
License: Python Software Foundation License
"""
from __future__ import print_function, division

def addvar(lowBound=0, var_count=[0], *args, **kwargs):
    """変数作成用ユーティリティ"""
    from pulp import LpVariable
    var_count[0] += 1
    return LpVariable('v%d' % var_count[0], lowBound=lowBound, *args, **kwargs)

def addvars(*n, **ad):
    """配列変数作成用ユーティリティ"""
    va = []
    addvarsRec(va, *n, **ad)
    return va

def addvarsRec(va, *n, **ad):
    if n == (): return None
    b = len(n) == 1
    for i in range(n[0]):
        if b:
            va.append(addvar(**ad))
        else:
            nva = []
            addvarsRec(nva, *n[1:], **ad)
            va.append(nva)

def addline(m, p1, p2, x, y, upper=True):
    """2点直線制約"""
    from pulp import LpConstraint, LpConstraintGE, LpConstraintLE
    dx = p2[0] - p1[0]
    if dx != 0:
        m += LpConstraint(y - (p2[1] - p1[1]) / dx * x - (p2[0] * p1[1] - p1[0] * p2[1]) / dx,
                          LpConstraintGE if upper else LpConstraintLE)

def addlines_conv(m, curve, x, y, upper=True):
    """区分線形制約(凸)"""
    from more_itertools import pairwise
    for p1, p2 in pairwise(curve):
        addline(m, p1, p2, x, y, upper)

def addlines(m, curve, x, y):
    """区分線形制約(非凸)"""
    from pulp import LpBinary, lpSum, lpDot
    n = len(curve)
    w = addvars(n)
    z = addvars(n, cat=LpBinary)
    a = [p[0] for p in curve]
    b = [p[1] for p in curve]
    m += x == a[0] + lpSum(w[:-1])
    c = [(b[i+1]-b[i]) / (a[i+1]-a[i]) for i in range(n-1)]
    m += y == b[0] + lpDot(c, w[:-1])
    for i in range(n-1):
        if i < n-2:
            m += (a[i+1]-a[i]) * z[i] <= w[i]
        m += w[i] <= (a[i+1]-a[i]) * (1 if i == 0 else z[i-1])

def value_or_zero(x):
    """value or 0"""
    from pulp import value
    v = value(x)
    return v if v is not None else 0

def graph_from_table(tb1, tb2, directed=False):
    import networkx as nx
    class mydict(dict):
        __getattr__ = dict.__getitem__
        __deepcopy__ = lambda i, j: mydict(i)
    g = nx.DiGraph() if directed else nx.Graph()
    for i, r in tb1.iterrows():
        g.add_node(r.id, mydict(r.to_dict()))
    for i, r in tb2.iterrows():
        g.add_edge(r.node1, r.node2, None)
        g.adj[r.node1][r.node2] = mydict(r.to_dict())
        (g.pred if directed else g.adj)[r.node2][r.node1] = g.adj[r.node1][r.node2]
    return g

def networkx_draw(g, dcpos=None, **kwargs):
    import networkx as nx
    if not dcpos:
        dcpos = {r.id:(r.x, r.y) for i, r in g.node.items()}
    nx.draw_networkx_nodes(g, dcpos, **kwargs)
    nx.draw_networkx_edges(g, dcpos)
    nx.draw_networkx_labels(g, dcpos)
    return dcpos

def maximum_stable_set(g, weight='weight'):
    """
    最大安定集合問題
    入力
        g: グラフ(node:weight)
        weight: 重みの属性文字
    出力
        最大安定集合の重みの合計と頂点番号リスト
    """
    from pulp import LpProblem, LpMaximize, LpBinary, lpDot, lpSum, value
    m = LpProblem(sense=LpMaximize)
    v = [addvar(cat=LpBinary) for _ in g.nodes()]
    for i, j in g.edges():
        m += v[i] + v[j] <= 1
    m += lpDot([g.node[i].get(weight, 1) for i in g.nodes()], v)
    if m.solve() != 1: return None
    return value(m.objective), [i for i, x in enumerate(v) if value(x) > 0.5]

def maximum_cut(g, weight='weight'):
    """
    最大カット問題
    入力
        g: グラフ(node:weight)
        weight: 重みの属性文字
    出力
        カットの重みの合計と片方の頂点番号リスト
    """
    from pulp import LpProblem, LpMaximize, LpBinary, lpDot, lpSum, value
    m = LpProblem(sense=LpMaximize)
    v = [addvar(cat=LpBinary) for _ in g.nodes()]
    u = []
    for i in range(g.number_of_nodes()):
        for j in range(i + 1, g.number_of_nodes()):
            w = g.get_edge_data(i, j, {weight:None}).get(weight, 1)
            if w:
                t = addvar()
                u.append(w * t)
                m += t <= v[i] + v[j]
                m += t <= 2 - v[i] - v[j]
    m += lpSum(u)
    if m.solve() != 1: return None
    return value(m.objective), [i for i, x in enumerate(v) if value(x) > 0.5]

def min_node_cover(g, weight='weight'):
    """
    最小頂点被覆問題
    入力
        g: グラフ
        weight: 重みの属性文字
    出力
        頂点リスト
    """
    return list(set(g.nodes()) - set(maximum_stable_set(g)[1]))

def vrp(g, nv, capa, demand='demand', cost='cost'):
    """
    運搬経路問題
    入力
        g: グラフ(node:demand, edge:cost)
        nv: 運搬車数
        capa: 運搬車容量
        demand: 需要の属性文字
        cost: 費用の属性文字
    出力
        運搬車ごとの頂点対のリスト
    """
    from pulp import LpProblem, LpBinary, lpDot, lpSum, value
    rv = range(nv)
    m = LpProblem()
    x = [{(i, j):addvar(cat=LpBinary) for i, j in g.edges()} for _ in rv]
    w = [[addvar() for i in g.nodes()] for _ in rv]
    m += lpSum(g.adj[i][j][cost] * lpSum(x[v][i, j] for v in rv) for i, j in g.edges())
    for v in rv:
        xv, wv = x[v], w[v]
        m += lpSum(xv[0, j] for j in g.nodes() if j) == 1
        for h in g.nodes():
            m += wv[h] <= capa
            m += lpSum(xv[i, j] for i, j in g.edges() if i == h) \
              == lpSum(xv[i, j] for i, j in g.edges() if j == h)
        for i, j in g.edges():
            if i == 0:
                m += wv[j] >= g.node[j][demand] - capa * (1 - xv[i, j])
            else:
                m += wv[j] >= wv[i] + g.node[j][demand] - capa * (1 - xv[i, j])
    for h in g.nodes()[1:]:
        m += lpSum(x[v][i, j] for v in rv for i, j in g.edges() if i == h) == 1
    if m.solve() != 1: return None
    return [[(i, j) for i, j in g.edges() if value(x[v][i, j]) > 0.5] for v in rv]

def tsp(point):
    """
    巡回セールスマン問題
        全探索
    入力
        point: 座標のリスト
    出力
        点番号リスト
    """
    from math import sqrt
    from itertools import permutations
    n = len(point)
    bst, mn, r = None, 1e100, range(1, n)
    for d in permutations(r):
        e = [point[i] for i in [0] + list(d) + [0]]
        s = sqrt(sum((e[i][0] - e[i + 1][0])**2
                   + (e[i][1] - e[i + 1][1])**2 for i in range(n)))
        if s < mn:
            mn = s
            bst = [0] + list(d)
    return bst

class Autodict:
    def __init__(self):
        self.dict = {}
        self.keys = []
    def __getitem__(self, key):
        if key not in self.dict:
            self.dict[key] = len(self.dict)
            self.keys.append(key)
        return self.dict[key]
def set_covering(n, cand, is_partition=False):
    """
    集合被覆問題
    入力
        n: 要素数
        cand: (重み, 部分集合)の候補リスト
    出力
        選択された候補リストの番号リスト
    """
    ad = Autodict()
    from pulp import LpProblem, LpBinary, lpDot, lpSum, value
    m = LpProblem()
    vv = [addvar(cat=LpBinary) for _ in cand]
    m += lpDot([w for w, _ in cand], vv) # obj func
    ee = [[] for _ in range(n)]
    for v, (_, c) in zip(vv, cand):
        for k in c: ee[ad[k]].append(v)
    for e in ee:
        if e:
            if is_partition:
                m += lpSum(e) == 1
            else:
                m += lpSum(e) >= 1
    if m.solve() != 1: return None
    return [i for i, v in enumerate(vv) if value(v) > 0.5]

def set_partition(n, cand):
    """
    集合分割問題
    入力
        n: 要素数
        cand: (重み, 部分集合)の候補リスト
    出力
        選択された候補リストの番号リスト
    """
    return set_covering(n, cand, True)

def two_machine_flowshop(p):
    """
    2機械フローショップ問題
        2台のフローショップ型のジョブスケジュールを求める(ジョンソン法)
    入力
        p: (前工程処理時間, 後工程処理時間)の製品ごとのリスト
    出力
        処理時間と処理順のリスト
    """
    from numpy import array, inf
    def proctime(p, l):
        n = len(p)
        t = [[0, 0] for _ in range(n + 1)]
        for i in range(1, n + 1):
            t1, t2 = p[l[i - 1]]
            t[i][0] = t[i - 1][0] + t1
            t[i][1] = max(t[i - 1][1], t[i][0]) + t2
        return t[n][1]
    a, l1, l2 = array(p, dtype=float).flatten(), [], []
    for _ in range(a.size // 2):
        j = a.argmin()
        k = j // 2
        if j % 2 == 0:
            l1.append(k)
        else:
            l2.append(k)
        a[2 * k] = a[2 * k + 1] = inf
    l = l1 + l2[::-1]
    return proctime(p, l), l

def shift_scheduling(ndy, nst, shift, proh, need):
    """
    勤務スケジューリング問題
    入力
        ndy: 日数
        nst: スタッフ数
        shift: シフト(1文字)のリスト
        proh: 禁止パターン(シフトの文字列)のリスト
        need: シフトごとの必要人数リスト(日ごと)
    出力
        日ごとスタッフごとのシフトの番号のテーブル
    """
    from pulp import LpProblem, LpBinary, lpDot, lpSum, value
    nsh = len(shift)
    rdy, rst, rsh = range(ndy), range(nst), range(nsh)
    dsh = {sh:k for k, sh in enumerate(shift)}
    m = LpProblem()
    v = [[[addvar(cat=LpBinary) for _ in rsh] for _ in rst] for _ in rdy]
    for i in rdy:
        for j in rst:
            m += lpSum(v[i][j]) == 1
        for sh, dd in need.items():
            m += lpSum(v[i][j][dsh[sh]] for j in rst) >= dd[i]
    for prh in proh:
        n, pr = len(prh), [dsh[sh] for sh in prh]
        for j in rst:
            for i in range(ndy - n + 1):
                m += lpSum(v[i + h][j][pr[h]] for h in range(n)) <= n - 1
    if m.solve() != 1: return None
    return [[int(value(lpDot(rsh, v[i][j]))) for j in rst] for i in rdy]

def knapsack(size, weight, capacity):
    """
    ナップサック問題
        価値の最大化
    入力
        size: 荷物の大きさのリスト
        weight: 荷物の価値のリスト
        capacity: 容量
    出力
        価値の総和と選択した荷物番号リスト
    """
    from pulp import LpProblem, LpMaximize, LpBinary, lpDot, lpSum, value
    m = LpProblem(sense=LpMaximize)
    v = [addvar(cat=LpBinary) for _ in size]
    m += lpDot(weight, v)
    m += lpDot(size, v) <= capacity
    if m.solve() != 1: return None
    return value(m.objective), [i for i in range(len(size)) if value(v[i]) > 0.5]

def binpacking(c, w):
    """
    ビンパッキング問題
        列生成法で解く(近似解法)
    入力
        c: ビンの大きさ
        w: 荷物の大きさのリスト
    出力
        ビンごとの荷物の大きさリスト
    """
    from pulp import LpProblem, LpAffineExpression, \
         LpMinimize, LpMaximize, LpBinary, lpDot, lpSum, value
    n = len(w)
    rn = range(n)
    mkp = LpProblem('knapsack', LpMaximize) # 子問題
    mkpva = [addvar(cat=LpBinary) for _ in rn]
    mkp.addConstraint(lpDot(w, mkpva) <= c)
    mdl = LpProblem('dual', LpMaximize) # 双対問題
    mdlva = [addvar() for _ in rn]
    for i, v in enumerate(mdlva): v.w = w[i]
    mdl.setObjective(lpSum(mdlva))
    for i in rn:
        mdl.addConstraint(mdlva[i] <= 1)
    while True:
        mdl.solve()
        mkp.setObjective(lpDot([value(v) for v in mdlva], mkpva))
        mkp.solve()
        if mkp.status != 1 or value(mkp.objective) < 1 + 1e-6: break
        mdl.addConstraint(lpDot([value(v) for v in mkpva], mdlva) <= 1)
    nwm = LpProblem('primal', LpMinimize) # 主問題
    nm = len(mdl.constraints)
    rm = range(nm)
    nwmva = [addvar(cat=LpBinary) for _ in rm]
    nwm.setObjective(lpSum(nwmva))
    dict = {}
    for v, q in mdl.objective.items():
        dict[v] = LpAffineExpression() >= q
    const = list(mdl.constraints.values())
    for i, q in enumerate(const):
        for v in q:
            dict[v].addterm(nwmva[i], 1)
    for q in dict.values(): nwm.addConstraint(q)
    nwm.solve()
    if nwm.status != 1: return None
    w0, result = list(w), [[] for _ in range(len(const))]
    for i, va in enumerate(nwmva):
        if value(va) < 0.5: continue
        for v in const[i]:
            if v.w in w0:
                w0.remove(v.w)
                result[i].append(v.w)
    return [r for r in result if r]

class TwoDimPacking:
    """
    2次元パッキング問題
        ギロチンカットで元板からアイテムを切り出す(近似解法)
    入力
        width, height: 元板の大きさ
        items: アイテムの(横,縦)のリスト
    出力
        容積率と入ったアイテムの(横,縦,x,y)のリスト
    """
    def __init__(self, width, height, items=None):
        self.width = width
        self.height = height
        self.items = items
    @staticmethod
    def calc(pp, w, h):
        plw, plh, ofw, ofh = pp
        if w > plw or h > plh: return None
        if w * (plh - h) <= h * (plw - w):
            return (w * (plh - h), (w, plh - h, ofw, ofh + h), (plw - w, plh, ofw + w, ofh))
        else: return (h * (plw - w), (plw - w, h, ofw + w, ofh), (plw, plh - h, ofw, ofh + h))
    def solve(self, iters=100):
        from random import shuffle, seed
        bst, self.pos = 0, []
        seed(1)
        for cnt in range(iters):
            tmp, szs, plates = [], list(self.items), [(self.width, self.height, 0, 0)]
            shuffle(szs)
            while len(szs) > 0 and len(plates) > 0:
                mni, mnr, (w, h), szs = -1, [1e9], szs[0], szs[1:]
                for i in range(len(plates)):
                    res = TwoDimPacking.calc(plates[i], w, h)
                    if res and res[0] < mnr[0]: mni, mnr = i, res
                if mni >= 0:
                    tmp.append((w, h) + plates[i][2:])
                    plates[i:i + 1] = [p for p in mnr[1: 3] if p[0] * p[1] > 0]
            sm = sum(r[0] * r[1] for r in tmp)
            if sm > bst: bst, self.result = sm, tmp
        self.rate = bst / self.width / self.height
        return self.rate, self.result

def facility_location(p, point, cand):
    """
    施設配置問題
        P-メディアン問題：総距離×量の和の最小化
    入力
        p: 施設数上限
        point: 顧客位置と量のリスト
        cand: 施設候補位置と容量のリスト
    出力
        顧客ごとの施設番号リスト
    """
    from math import sqrt
    from pulp import LpProblem, LpBinary, lpDot, lpSum, value
    if not cand: cand = point
    rp, rc = range(len(point)), range(len(cand))
    m = LpProblem()
    x = [[addvar(cat=LpBinary) for _ in cand] for _ in point]
    y = [addvar(cat=LpBinary) for _ in cand]
    m += lpSum(x[i][j] * point[i][2] * sqrt((point[i][0] - cand[j][0])**2
        + (point[i][1] - cand[j][1])**2) for i in rp for j in rc)
    m += lpSum(y) <= p
    for i in rp:
        m += lpSum(x[i]) == 1
    for j in rc:
        m += lpSum(point[i][2] * x[i][j] for i in rp) <= cand[j][2] * y[j]
    if m.solve() != 1: return None
    return [int(value(lpDot(rc, x[i]))) for i in rp]

def facility_location_without_capacity(p, point, cand=None):
    """
    容量制約なし施設配置問題
        P-メディアン問題：総距離の和の最小化
    入力
        p: 施設数上限
        point: 顧客位置のリスト
        cand: 施設候補位置のリスト(Noneの場合、pointと同じ)
    出力
        顧客ごとの施設番号リスト
    """
    from math import sqrt
    from pulp import LpProblem, LpBinary, lpDot, lpSum, value
    if not cand: cand = point
    rp, rc = range(len(point)), range(len(cand))
    m = LpProblem()
    x = [[addvar(cat=LpBinary) for _ in cand] for _ in point]
    y = [addvar(cat=LpBinary) for _ in cand]
    m += lpSum(x[i][j] * sqrt((point[i][0] - cand[j][0])**2
                            + (point[i][1] - cand[j][1])**2) for i in rp for j in rc)
    m += lpSum(y) <= p
    for i in rp:
        m += lpSum(x[i]) == 1
        for j in rc:
            m += x[i][j] <= y[j]
    if m.solve() != 1: return None
    return [int(value(lpDot(rc, x[i]))) for i in rp]

def quad_assign(quant, dist):
    """
    2次割当問題
        全探索
    入力
        quant: 対象間の輸送量
        dist: 割当先間の距離
    出力
        対象ごとの割当先番号リスト
    """
    from itertools import permutations
    n = len(quant)
    bst, mn, r = None, 1e100, range(n)
    for d in permutations(r):
        s = sum(quant[i][j] * dist[d[i]][d[j]] for i in r for j in r if j != i)
        if s < mn:
            mn = s
            bst = d
    return bst

def gap(cst, req, cap):
    """
    一般化割当問題
        費用最小の割当を解く
    入力
        cst: エージェントごと、ジョブごとの費用のテーブル
        req: エージェントごと、ジョブごとの要求量のテーブル
        cap: エージェントの容量のリスト
    出力
        ジョブごとのエージェント番号リスト
    """
    from pulp import LpProblem, LpBinary, lpDot, lpSum, value
    na, nj = len(cst), len(cst[0])
    m = LpProblem()
    v = [[addvar(cat=LpBinary) for _ in range(nj)] for _ in range(na)]
    m += lpSum(lpDot(cst[i], v[i]) for i in range(na))
    for i in range(na):
        m += lpDot(req[i], v[i]) <= cap[i]
    for j in range(nj):
        m += lpSum(v[i][j] for i in range(na)) == 1
    if m.solve() != 1: return None
    return [int(value(lpDot(range(na), [v[i][j] for i in range(na)]))) for j in range(nj)]

def stable_matching(prefm, preff):
    """
    安定マッチング問題
    入力
        prefm, preff: 選好
    出力
        マッチング
    """
    res, n = {}, len(prefm)
    pos, freem = [0] * n, list(range(n-1, -1, -1))
    while freem:
        m, freem = freem[-1], freem[:-1]
        if pos[m] == n: continue
        f, pos[m] = prefm[m][pos[m]], pos[m]+1
        if f in res:
            if preff[f].index(res[f]) < preff[f].index(m):
                freem.append(m)
                continue
            else: freem.append(res[f])
        res[f] = m
    return res
