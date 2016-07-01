#!/usr/bin/python
import copy
import sys
import time

def isInstalled():
    return 'yes'
    
class Face():
    def __init__(self, side_length):
        self.size = side_length
        self.squares = [[0 for __ in range(self.size)] for __ in range(self.size)]
    
    def done(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.squares[i][j] != self.squares[0][0]:
                    return False
        return True

    def __str__(self):
        return '\n'.join([' '.join(map(str, x)) for x in self.squares])
    
    def set_all(self, vals_to_set):
        for i in range(self.size):
            for j in range(self.size):
                self.squares[i][j] = vals_to_set[i*self.size + j]

    def get_row(self, i):
        return self.squares[i][:]
    
    def get_col(self, j):
        return [row[j] for row in self.squares]

    def set_row(self, i, row):
        for j, val in enumerate(row):
            self.squares[i][j] = val

    def set_col(self, j, col):
        for i, row in enumerate(self.squares):
            row[j] = col[i]

    def replace_row(self, i, row):
        ret = self.get_row(i)
        self.set_row(i, row)
        return ret
    
    def replace_col(self, j, col):
        ret = self.get_col(j)
        self.set_col(j, col)
        return ret

    def rotate(self, is_clockwise):
        squares = [[0 for __ in range(self.size)] for __ in range(self.size)]
        if is_clockwise:
            for i in range(self.size):
                for j in range(self.size):
                    squares[j][self.size - i - 1] = self.squares[i][j]
        else:
            for i in range(self.size):
                for j in range(self.size):
                    squares[self.size - j - 1][i] = self.squares[i][j]
        self.squares= squares

    def tuplify(self):
        return tuple([tuple(row) for row in self.squares])
    
class Cube():
    face_name = {0: 'front', 1: 'top', 2:'right', 3:'back', 4:'bottom', 5:'left'}
    face_number = {name:number for number, name in face_name.iteritems()}
    face_across = {x:(x + 3)%6 for x in range(6)}
    
    def __init__(self, side_length):
        self.size = side_length
        self.sides = [Face(self.size) for __ in range(6)]
    
    def side(self, side):
        return self.sides[self.face_number.get(side, side)]
    
    def rotate_nth_from_front(self, n, is_clockwise):
        if n == 0:
            self.side('front').rotate(is_clockwise)
        elif n == self.size - 1:
            self.side('back').rotate(1 - is_clockwise)
    
        mirror = self.size - n - 1
         
        col_from_left = self.side('left').get_col(mirror)
        row_from_top = self.side('top').get_row(mirror)
        col_from_right = self.side('right').get_col(n)
        row_from_bot = self.side('bottom').get_row(n)

        if is_clockwise:
            col_from_left.reverse()
            col_from_right.reverse()
            self.side('left').set_col(mirror, row_from_bot)
            self.side('top').set_row(mirror, col_from_left)
            self.side('right').set_col(n, row_from_top)
            self.side('bottom').set_row(n, col_from_right)
        else:
            row_from_top.reverse()
            row_from_bot.reverse()
            self.side('left').set_col(mirror, row_from_top)
            self.side('top').set_row(mirror, col_from_right)
            self.side('right').set_col(n, row_from_bot)
            self.side('bottom').set_row(n, col_from_left)

    def rotate_nth_from_back(self, n, is_clockwise):
        self.rotate_nth_from_front(self.size - n -1, 1 - is_clockwise) 

    def rotate_nth_from_right(self, n, is_clockwise):
        if n == 0:
            self.side('right').rotate(is_clockwise)
        elif n == self.size - 1:
            self.side('left').rotate(1 - is_clockwise)

        mirror = self.size - n -1

        col_from_front = self.side('front').get_col(mirror)
        col_from_top = self.side('top').get_col(mirror)
        col_from_back = self.side('back').get_col(n)
        col_from_bot = self.side('bottom').get_col(mirror)

        if is_clockwise:
            col_from_front.reverse()
            col_from_back.reverse()
            self.side('top').set_col(mirror, col_from_front)
            self.side('front').set_col(mirror, col_from_bot)
            self.side('bottom').set_col(mirror, col_from_back)
            self.side('back').set_col(n, col_from_top)
        else:
            col_from_bot.reverse()
            col_from_back.reverse()
            self.side('top').set_col(mirror, col_from_back)
            self.side('back').set_col(n, col_from_bot)
            self.side('bottom').set_col(mirror, col_from_front)
            self.side('front').set_col(mirror, col_from_top)

    def rotate_nth_from_left(self, n, is_clockwise):
        self.rotate_nth_from_right(self.size - n - 1, 1 - is_clockwise)

    def rotate_nth_from_top(self, n, is_clockwise):
        if n == 0:
            self.side('top').rotate(is_clockwise)
        elif n == self.size - 1:
            self.side('bottom').rotate(1 - is_clockwise)

        mirror = self.size - n - 1
    
        row_from_front = self.side('front').get_row(n)
        row_from_left = self.side('left').get_row(n)
        row_from_back = self.side('back').get_row(n)
        row_from_right = self.side('right').get_row(n)
        

        if is_clockwise:
            self.side('left').set_row(n, row_from_front)
            self.side('front').set_row(n, row_from_right)
            self.side('right').set_row(n, row_from_back)
            self.side('back').set_row(n, row_from_left)
        else:
            self.side('front').set_row(n, row_from_left)
            self.side('left').set_row(n, row_from_back)
            self.side('back').set_row(n, row_from_right)
            self.side('right').set_row(n, row_from_front)
        
    
    def rotate_nth_from_bottom(self, n, is_clockwise):
        self.rotate_nth_from_top(self.size - n - 1, 1 - is_clockwise)

    def tuplify(self):
        return tuple([self.side(i).tuplify() for i in range(6)])

    def done(self):
        for i in range(6):
            if not self.side(i).done():
                return False
        return True


    def solve2_a_star(self):
        vis = dict()
        now = copy.deepcopy(self)
        vis[now.tuplify()] = (-1, 'Start')
        queue = []
        queue.append(now)

        funcs = [Cube.rotate_nth_from_top, Cube.rotate_nth_from_front, Cube.rotate_nth_from_right]
        move_desc = ['top', 'front', 'right']
        directions = [(0, 'counter-clockwise'), (1, 'clockwise')]

        while queue:
            now = queue.pop(0)
            if now.done():
                break
            for f, desc in zip(funcs, move_desc):
                for d in directions:
                    cop = copy.deepcopy(now)
                    f(cop, 0, d[0])
                    if cop.tuplify() not in vis:
                        vis[cop.tuplify()] = (now, desc + ' ' + d[1])
                        queue.append(cop)
        ans = []
        while now.tuplify() != self.tuplify():
            ans.append(vis[now.tuplify()][1])
            now = vis[now.tuplify()][0]
        
        ans.reverse()
        return ans


    def solve2(self):
        vis = dict()
        
        now = copy.deepcopy(self)
        vis[now.tuplify()] = (-1, 'Start')
        queue = []
        queue.append((now, 0))

        funcs = [Cube.rotate_nth_from_top, Cube.rotate_nth_from_front, Cube.rotate_nth_from_right]
        move_desc = ['top', 'front', 'right']
        directions = [(0, 'counter-clockwise'), (1, 'clockwise')]
        depnow = -1
        while queue:
            now, dep = queue.pop(0)
            if dep > depnow:
                depnow = dep
                print depnow
            #print 'on top :'
            #out(now)
            #print ''
            done = 0
            if now.done():
                break
            for f, desc in zip(funcs, move_desc):
                for d in directions:
                    cop = copy.deepcopy(now)
                    f(cop, 0, d[0])
                    if cop.tuplify() not in vis:
                        #print 'appending with move : %s' % desc+ ' ' + d[1]
                        #out(cop)
                        vis[cop.tuplify()] = (now, desc + ' ' + d[1])
                        queue.append((cop, dep + 1))
                        if cop.done():
                            now = cop
                            done = 1
                            break
                    #else:
                    #    print 'already visited'
                    #    print 'appending with move : %s' % desc+ ' '+ d[1]
                    #    out(cop)
            #print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
            if done:
                break
        ans = []
        #while vis[now.tuplify()][0] != -1:
        while now.tuplify() != self.tuplify():
            #print 'now : '
            #out(now)
            #print ''
            ans.append(vis[now.tuplify()][1])
            #print 'move from dad : %s' % vis[now.tuplify()][1]
            #print 'dad : '
            now = vis[now.tuplify()][0]
            #out(now)
            #print ''
            #print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
            #print ''
        
        ans.reverse()
        return ans

colormap = dict(blue = 0, white = 1, red = 2, green = 3, yellow = 4, orange = 5)
inv_colormap = {str(v):k for k, v in colormap.iteritems()}
def out(c):
    for i in range(6):
        print c.face_name[i]
        for ch in c.side(i).__str__():
            sys.stdout.write(inv_colormap.get(ch, ch))
        print ''
        print ''
    print ''



def main():
    c = Cube(2)

    front = ['blue', 'green', 'blue', 'green']
    top = ['orange', 'red', 'orange', 'red']
    left = ['white', 'white', 'white', 'white']
    right = ['yellow', 'yellow', 'yellow', 'yellow']
    bottom = ['red', 'orange', 'red', 'orange']
    back = ['blue', 'green', 'blue', 'green']

    front = ['orange', 'orange', 'white', 'orange']
    top = ['green', 'blue', 'white', 'white']
    left = ['red', 'blue', 'red', 'green']
    right = ['green', 'white', 'green', 'orange']
    bottom = ['red', 'yellow', 'blue', 'blue']
    back = ['red', 'yellow', 'yellow', 'yellow']
    
#    front = ['white', 'orange', 'blue', 'orange']
#    top = ['green', 'green', 'red', 'blue']
#    left = ['white', 'blue', 'red', 'yellow']
#    right = ['white', 'yellow', 'white', 'orange']
#    bottom = ['orange', 'green', 'blue', 'yellow']
#    back = ['red', 'red', 'green', 'yellow']
    
    front = ['white', 'yellow', 'blue', 'green']
    top = ['orange', 'orange', 'red', 'red']
    left = ['white', 'blue', 'green', 'yellow']
    right = ['blue', 'white', 'yellow', 'green']
    bottom = ['orange', 'orange', 'red', 'red']
    back = ['blue', 'green', 'white', 'yellow']
    
    
    c.side('front').set_all([colormap[color] for color in front])
    c.side('back').set_all([colormap[color] for color in back])
    c.side('left').set_all([colormap[color] for color in left])
    c.side('right').set_all([colormap[color] for color in right])
    c.side('top').set_all([colormap[color] for color in top])
    c.side('bottom').set_all([colormap[color] for color in bottom])

    cl = time.clock()
    for move in c.solve2():
        print move
    print time.clock() - cl

if __name__ == '__main__':
    main()        
