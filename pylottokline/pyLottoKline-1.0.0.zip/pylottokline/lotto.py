import numpy as np
import os
import collections

import lunar

class Xuanhao(object):
    colors = [[1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46], # 红(17)
              [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49],   # 绿(16)
              [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]]    # 篮(16)
              
    wuxing = [[],[],[],[],[]] # 五行
              
    def __init__(self):
        self.nl_year_sx = lunar.Lunar().sx_year()
        self.current_sx_string = self.get_sx_string(self.nl_year_sx) # 当年生肖序列串，如：鸡猴羊马蛇龙兔虎牛鼠猪狗
        #print(self.current_sx_string)
        
        self.current_up_numbers =  [] # 当前指标向上号码 -----|
        self.current_down_numbers = [] # 当前指标向下号码     |----> 这三个用于选号
        self.all_numbers = {} # 所有选中的指标对应的号码 -----|
        
        self.curent_qishu = None # 当前期数 （需要联网）
        self.curent_zb_name = None # 当前指标名称
        
        self.zb_funcs = {'ptsx':self.ptsx,
                        'ptws':self.ptws,
                        'mod':self.mod,
                        'fen':self.fen,
                        'ls':self.ls,
                        'kd':self.kd,
                        'ws':self.ws,
                        'hs':self.hs,
                        'bs':self.bs,
                        'lx':self.lx,
                        'wx':self.wx,
                        'jl':self.jl,
                        'yqc':self.yqc,
                        'pre':self.pre,
                        'hot':self.hot,
                        'rnd':self.rnd,
                        'fom':self.fom}
        
    def get_last_draw(self):
        '''取最新一期数据'''
        url = 'http://www.5457.com/chajian/bmjg.js'
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            #'If-Modified-Since': 'Tue, 19 Jan 2016 13:34:53 GMT'
        }

        r = requests.get(url, headers=headers)
        dic = r.json() # {"k":"008,39,25,30,08,20,18,13,009,01,21,四,21点30分","t":"1000","联系":"QQ：7136995"}
        #haoma = dic['k'].split(',')[:8] # ['008','39','25','30','08','20','18','13']
        #haoma = [int(x) for x in dic['k'].split(',')[:8]]
        #qishu, *draw = haoma
        qishu, draw = int(dic['k'].split(',')[0]), dic['k'].split(',')[1:8]
        return qishu, draw
        
    def make_real_history(self, periods=500, filename='history.csv', lotto_type='MS'):
        '''生成真实历史数据'''
        filename = os.path.join(os.path.dirname(__file__), filename)
        history = np.genfromtxt(filename, delimiter=',')
        
        self.dataframe = history[-periods:,1:-1].astype(int)
        self.n_periods = self.dataframe.shape[0]

    
    
    # ==========================================
    # 下面都是选号函数
    # ['mod','fen','ls','kd','ws','hs','bs','lx','wx','jl','yqc','pre','hot','rnd','fom']
    # ==========================================
    def xh_mod(self, up_down=1, m=2, mod_list=None):
        '''模数选号(验证，即弃)'''
        if up_down == 1:
            x = np.array(list(set(filter(lambda x:self.mod(x, m, mod_list), range(1,50)))))
            return x[np.argsort(x)]
        else:
            x = np.array(list(set(range(1,50)) - set(filter(lambda x:self.mod(x, m, mod_list), range(1,50)))))
            return x[np.argsort(x)]
            
        
    def xh(self, zb_func, up_down=1, *args, **kwargs):
        '''选号'''
        if up_down == 1:
            res = np.array(list(set(filter(lambda x:zb_func(x, *args, **kwargs), range(1,50)))))
            return res[np.argsort(res)]
        else:
            res = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, *args, **kwargs), range(1,50)))))
            return res[np.argsort(res)]

        
    def tongji(self, numbers_list):
        '''统计选号各个指标出现的次数'''
        c = np.array(collections.Counter(numbers_list).most_common())  # 大于0次
        c0 = np.array([(x,0) for x in set(range(1,50)) - set(c[:,0])]) # 0次
        r = np.vstack((c, c0))
        res = {}
        for k in np.unique(r[:,1]):
            v = r[:,0][np.where(r[:,1]==k)] # 黑科技！
            res.update({k:list(v)})
        return res
    
    # ==========================================
    # 下面是各个指标函数
    # ==========================================
    def adapter(self, zb_func, column, **kwargs):
        '''指标适配器，生成指标序列'''
        res = []
        if 0 < column < 8: # 参数：column=7, m=2, f=2, ...
            if zb_func.__name__ not in ['jl', 'yqc', 'pre', 'hot']:
                series = self.dataframe[:, column-1]
                #return np.apply_along_axis(zb_func, 0, series, **kwargs)
                for x in series:
                    res.append(int(zb_func(x, **kwargs)))
                
                # 最后，把号码也对应得到
                up = np.array(list(set(filter(lambda x:zb_func(x, **kwargs), range(1,50))))) #向上
                self.current_up_numbers = up[np.argsort(up)]
                down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, **kwargs), range(1,50))))) #向下
                self.current_down_numbers = down[np.argsort(down)]
            elif zb_func.__name__ in ['jl', 'yqc']: # 参数：column2=7, pre_n=1
                column2, pre_n = kwargs['column2'], kwargs['pre_n']
                series = self.dataframe[:, column-1]
                series2 = self.dataframe[:, column2-1]
                for i in range(len(series)):
                    num = series[i]
                    if i < pre_n:
                        pre_num = 0 # 这个只考虑yqc, 没管jl了==!!!
                    else:
                        pre_num = series2[i-pre_n]
                    res.append(zb_func(num, pre_num))
                    
                # 最后，把号码也对应得到
                up = np.array(list(set(filter(lambda x:zb_func(x, pre_num), range(1,50))))) #向上
                self.current_up_numbers = up[np.argsort(up)]
                down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, pre_num), range(1,50))))) #向下
                self.current_down_numbers = down[np.argsort(down)]
            elif zb_func.__name__ in ['pre', 'hot']: # 参数： column2=7, pre_n=1, pre_len=49, (jiaquan_type='xx')
                column2, pre_n, pre_len = kwargs['column2'], kwargs['pre_n'], kwargs['pre_len']
                jiaquan_type = kwargs.get('jiaquan_type', None)
                
                series = self.dataframe[:, column-1]
                series2 = self.dataframe[:, column2-1]
                for i in range(len(series)):
                    num = series[i]
                    if i < pre_n:
                        pre_list = []
                    elif i < pre_n + pre_len - 1:
                        pre_list = series2[:i-pre_n]
                    else:
                        pre_list = series2[i-(pre_n+pre_len)+1:i-pre_n]
                    if jiaquan_type is None:
                        res.append(zb_func(num, pre_list))
                    else:
                        res.append(zb_func(num, pre_list, jiaquan_type))
                        
                # 最后，把号码也对应得到
                if jiaquan_type is None:
                    up = np.array(list(set(filter(lambda x:zb_func(x, pre_list), range(1,50))))) #向上
                    self.current_up_numbers = up[np.argsort(up)]
                    down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, pre_list), range(1,50))))) #向下
                    self.current_down_numbers = down[np.argsort(down)]
                else:
                    up = np.array(list(set(filter(lambda x:zb_func(x, pre_list, jiaquan_type), range(1,50))))) #向上
                    self.current_up_numbers = up[np.argsort(up)]
                    down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, pre_list, jiaquan_type), range(1,50))))) #向下
                    self.current_down_numbers = down[np.argsort(down)]
        elif column == 0:  # 平特生肖、平特尾数
            dataframe = self.dataframe
            #return np.apply_along_axis(zb_func, 1, dataframe, **kwargs)
            for x in dataframe:
                res.append(int(zb_func(x, **kwargs)))
        return np.where(np.array(res)==0, -1, 1)
        
        
    def adapter2(self, zb_name, *args):
        '''指标适配器，生成指标序列'''
        # ['mod','fen','ls','kd','ws','hs','bs','lx','wx','jl','yqc','pre','hot','rnd','fom']
        zb_func = self.zb_funcs[zb_name]
        
        res = []
        if zb_name in ['rnd']:
            column, = args

            tmp = np.arange(1, 50)
            np.random.shuffle(tmp)
            random_list = tmp[:24]
            
            series = self.dataframe[:, column-1]
            for x in series:
                res.append(zb_func(x, random_list))
                
            # 最后，把号码也对应得到
            up = np.array(list(set(filter(lambda x:zb_func(x, random_list), range(1,50))))) #向上
            self.current_up_numbers = up[np.argsort(up)]
            down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, random_list), range(1,50))))) #向下
            self.current_down_numbers = down[np.argsort(down)]
        elif zb_name in ['ls','kd']:
            column, = args
            series = self.dataframe[:, column-1]
            for x in series:
                res.append(zb_func(x))
            
            # 最后，把号码也对应得到
            up = np.array(list(set(filter(lambda x:zb_func(x), range(1,50))))) #向上
            self.current_up_numbers = up[np.argsort(up)]
            down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x), range(1,50))))) #向下
            self.current_down_numbers = down[np.argsort(down)]
        elif zb_name in ['mod','fen','ws','hs','bs','lx','wx']:
            column, canshu1 = args
            series = self.dataframe[:, column-1]
            for x in series:
                res.append(zb_func(x, canshu1))
            
            # 最后，把号码也对应得到
            up = np.array(list(set(filter(lambda x:zb_func(x, canshu1), range(1,50))))) #向上
            self.current_up_numbers = up[np.argsort(up)]
            down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, canshu1), range(1,50))))) #向下
            self.current_down_numbers = down[np.argsort(down)]
        elif zb_name in ['jl', 'yqc']:
            column, column2, pre_n = args
            series = self.dataframe[:, column-1]
            series2 = self.dataframe[:, column2-1]
            for i in range(len(series)):
                num = series[i]
                if i < pre_n:
                    pre_num = 0 # 这个只考虑yqc, 没管jl了==!!!
                else:
                    pre_num = series2[i-pre_n]
                res.append(zb_func(num, pre_num))
                
            # 最后，把号码也对应得到
            up = np.array(list(set(filter(lambda x:zb_func(x, pre_num), range(1,50))))) #向上
            self.current_up_numbers = up[np.argsort(up)]
            down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, pre_num), range(1,50))))) #向下
            self.current_down_numbers = down[np.argsort(down)]
        elif zb_name in ['pre']:
            column, column2, pre_n, pre_len = args
            
            series = self.dataframe[:, column-1]
            series2 = self.dataframe[:, column2-1]
            for i in range(len(series)):
                num = series[i]
                if i < pre_n:
                    pre_list = []
                elif i < pre_n + pre_len - 1:
                    pre_list = series2[:i-pre_n]
                else:
                    pre_list = series2[i-(pre_n+pre_len)+1:i-pre_n]
                res.append(zb_func(num, pre_list))
                    
            # 最后，把号码也对应得到
            up = np.array(list(set(filter(lambda x:zb_func(x, pre_list), range(1,50))))) #向上
            self.current_up_numbers = up[np.argsort(up)]
            down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, pre_list), range(1,50))))) #向下
            self.current_down_numbers = down[np.argsort(down)]
        elif zb_name in ['hot']:
            column, column2, pre_n, pre_len, jiaquan_type = args
            
            series = self.dataframe[:, column-1]
            series2 = self.dataframe[:, column2-1]
            for i in range(len(series)):
                num = series[i]
                if i < pre_n:
                    pre_list = []
                elif i < pre_n + pre_len - 1:
                    pre_list = series2[:i-pre_n]
                else:
                    pre_list = series2[i-(pre_n+pre_len)+1:i-pre_n]
                res.append(zb_func(num, pre_list, jiaquan_type))
                    
            # 最后，把号码也对应得到
            up = np.array(list(set(filter(lambda x:zb_func(x, pre_list, jiaquan_type), range(1,50))))) #向上
            self.current_up_numbers = up[np.argsort(up)]
            down = np.array(list(set(range(1,50)) - set(filter(lambda x:zb_func(x, pre_list, jiaquan_type), range(1,50))))) #向下
            self.current_down_numbers = down[np.argsort(down)]
        elif zb_name in ['ptsx', 'ptws']:  # 平特生肖、平特尾数
            canshu1, = args
            dataframe = self.dataframe
            for x in dataframe:
                res.append(zb_func(x, canshu1))
        return np.where(np.array(res)==0, -1, 1)
        
        
    def add_current_numbers(self, up_or_down):
        '''添加当前指标号码（根据给定的上/下方向）'''
        if up_or_down == 1:
            self.all_numbers[self.curent_zb_name + '_up'] = self.current_up_numbers
        elif up_or_down == -1:
            self.all_numbers[self.curent_zb_name + '_down'] = self.current_down_numbers
        
    def view_all_numbers(self):
        '''统计选号各个指标出现的次数'''
        numbers_list = np.hstack(self.all_numbers.values())

        #numbers_list = [x.tolist() for x in self.all_numbers.values()]
        #print(type(numbers_list), numbers_list)
        c = np.array(collections.Counter(numbers_list).most_common())  # 大于0次
        c0 = np.array([(x,0) for x in set(range(1,50)) - set(c[:,0])]) # 0次
        r = np.vstack((c, c0))
        res = {}
        for k in np.unique(r[:,1]):
            v = r[:,0][np.where(r[:,1]==k)] # 黑科技！
            res.update({k:list(v)})
            
        print(res)
        return res

        
        
    def tf(self, series, pre_n=1):
        '''同反'''
        pre_res = np.repeat(np.array([-1]), pre_n)
        res = np.where(series[:-pre_n] == series[pre_n:], 1, -1)
        return np.hstack((pre_res, res))
    
    # ==========================================
    # 下面都是各个指标函数
    # ['mod','fen','ls','kd','ws','hs','bs','sx','wx','jl','yqc','pre','hot','rnd','fom']
    # ==========================================
    def mod(self, num, m=2):
        '''模数'''
        #if mod_list is None:
        if m % 2 == 0:
            mod_list = list(range(m//2, m))
        else:
            mod_list = [i for i in range(m) if i%2 != m%2]
        mod_res = num % m
        #if isinstance(mod_res, np.ndarray): return mod_res # 很奇怪的效果，# apply_along_axis专用
        return 1 if mod_res in mod_list else 0   # 这里是0，方便选号。列操作时改回-1
        
        
    def fen(self, num, f=2):
        '''分数'''
        #if fen_list is None:
        fen_list = [i for i in range(f) if i%2 != f%2]
        return 1 if num // ((49 + 1) / f) in fen_list else 0
        
        
    def ls(self, num):
        '''路数'''
        # 单零路
        shi, ge = [num // 10, num % 10]
        return 1 if (shi % 3) * (ge % 3) == 0 and (shi % 3) + (ge % 3) != 0 else 0

        
    def kd(self, num):
        '''跨度'''
        wei = [num // 10, num % 10]
        return 0 if 0 < max(wei) - min(wei) < 4 else 1

        
    def ws(self, num, ws_type='dx'):
        '''尾数'''
        if ws_type == 'dx':
            ws_list = [5,6,7,8,9]
        elif ws_type == 'zh':
            ws_list = [1,2,3,5,7]
        return 1 if num % 10 in ws_list else 0
       
       
    def hs(self, num, hs_type='hdx'):
        '''和数'''
        # 四种情况：和数大小dx，和数单双ds，和数尾数大小wsdx，和数尾数质合wszh ['hdx', 'hds', 'hwd', 'hwz']
        hs_sum = sum([num // 10, num % 10])
        if hs_type == 'hdx':    # 和数大小dx
            return 1 if hs_sum > (4 + 9) / 2 else 0 # 最大号码49的两个数字之和
        elif hs_type == 'hds':  # 和数单双ds
            return self.mod(hs_sum)            
        elif hs_type == 'hwd':  # 和数尾数大小wsdx
            return self.ws(hs_sum)            
        elif hs_type == 'hwz':  # 和数尾数质合wszh
            return self.ws(hs_sum, ws_type='zh')
            
            
    def lx(self, num, jia_sx = '牛马羊鸡狗猪', nl_year_sx=None):
        '''六肖'''
        sx = '鼠牛虎兔龙蛇马羊猴鸡狗猪'

        if nl_year_sx is None:
            nl_year_sx = self.nl_year_sx
        
        ix = sx.index(nl_year_sx)
        if ix<11:
            tmp_sx = sx[ix+2:] + sx[:ix+2]
        else:
            tmp_sx = sx[1:] + sx[0]
        new_sx = list(tmp_sx)
        new_sx.reverse()
        
        return 1 if new_sx[num%12] in jia_sx else 0
        
        
    def bs(self, num, current_color='g'):
        '''波色'''
        ix = 'rgb'.index(current_color)
        return 1 if num not in self.colors[ix] else 0
        
    
    def wx(self, num, current_wx='jm'):
        '''五行'''
        ix1 = 'jmsht'.index(current_wx[0])
        ix2 = 'jmsht'.index(current_wx[1])
        return 1 if num not in self.wuxing[ix1] + self.wuxing[ix2] else 0
    
    
    def jl(self, num, num_pre):
        '''距离'''
        # 相对指标
        max_number = 49
        return 1 if max_number/4 < np.abs(num - num_pre) < 3 * max_number/4 else 0

    
    def yqc(self, num, num_pre):
        '''与前差'''
        # 相对指标
        return 1 if num > num_pre else 0


    def pre(self, num, list_pre):
        '''在前期'''
        # 相对指标
        return 1 if num in list_pre else 0

    
    def hot(self, num, list_pre, jiaquan_type='xx'):
        '''冷热'''
        # 相对指标
        # 四种情况：线性加权，泰勒加权，指数加权，简单计数 ['xx', 'tl', 'zs', 'js']
        n_numbers = 49 # 号码个数

        tmp = [0] * n_numbers
        for i, x in enumerate(list_pre):
            if jiaquan_type == 'xx':
                tmp[x-1] += i / sum(range(n_numbers))
            elif jiaquan_type == 'tl':
                tmp[x-1] += 1 / (n_numbers - i + 1)
            elif jiaquan_type == 'zs':
                tmp[x-1] += 1 / 2**(n_numbers - i)
            else:
                tmp[x-1] += 1 

        tmp = list(zip(range(1,50), tmp))
        tmp.sort(key=lambda x:x[1], reverse=True)
        ttmp = [x[0] for x in tmp[:n_numbers//2]] # 找出最热的24个数
        
        return 1 if num in ttmp else 0

        
    def rnd(self, num, random_list):
        '''随机'''
        return 1 if num in random_list else 0

    
    def fom(self, column, formula_text=''):
        '''公式formula'''
        # 相对指标
        pass
    
    
    # 平特生肖尾数
    def ptsx(self, draw, sx_ix=1):
        '''平特生肖'''
        return 1 if sx_ix in np.mod(draw, 12) else 0
        
    def ptws(self, draw, ws_ix=1):
        '''平特尾数'''
        return 1 if ws_ix in np.mod(draw, 10) else 0
        
        
    def get_sx_string(self, nl_year_sx=None):
        '''生成当年生肖序列'''
        sx = '鼠牛虎兔龙蛇马羊猴鸡狗猪'
        #jia_sx = '牛马羊鸡狗猪'
        
        if nl_year_sx is None:
            nl_year_sx = self.nl_year_sx
        
        ix = sx.index(nl_year_sx)
        if ix<11:
            tmp_sx = sx[ix+2:] + sx[:ix+2]
        else:
            tmp_sx = sx[1:] + sx[0]
        new_sx = list(tmp_sx)
        new_sx.reverse()
        return ''.join(new_sx)  # 鸡猴羊马蛇龙兔虎牛鼠猪狗
    
    
if __name__ == '__main__':
    lt = Xuanhao() 