#coding=utf8
import locale
locale.setlocale(locale.LC_ALL, '')
import curses
class Board:
    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(1)
        self.screen.nodelay(1)
        curses.start_color()
        self.screen.refresh()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.cache_size = 10
        self.cache_lines = []

    def init_match(self, game):
        self.cache_lines = []
        self.screen.erase()
        self.draw_header(game["t_name1"],game["t_name2"])

    def draw_status(self, status):
        self.screen.addstr(0, 2, status, curses.color_pair(1))
        self.screen.refresh()

    def draw_menu(self, games):
        self.screen.erase()
        self.screen.addstr(1, 25, '近期比赛', curses.color_pair(2))
        x, y = 3, 2
        for i, g in enumerate(games):
            self.screen.addstr(x, y, '[%d]' % (i+1,), curses.color_pair(1))
            self.screen.addstr(x, y+5, g['t_name1'], curses.color_pair(1))
            self.screen.addstr(x, y+20, g['n1'], curses.color_pair(1))
            self.screen.addstr(x, y+30, g['n2'], curses.color_pair(1))
            self.screen.addstr(x, y+40, g['t_name2'], curses.color_pair(1))
            x += 2
        self.screen.refresh()

    def draw_header(self, home, away):
        teamstr = '主队: %s    客队: %s' % (home, away)
        self.screen.addstr(0, 5, teamstr, curses.color_pair(2))
        x, y = 2, 1
        self.screen.addstr(x, y, '本节剩余', curses.color_pair(2))
        self.screen.addstr(x, y+9, '当前比分', curses.color_pair(2))
        self.screen.addstr(x, y+19, '球队', curses.color_pair(2))
        self.screen.addstr(x, y+25, '比赛信息', curses.color_pair(2))

    def update(self, msgs):
        x, y = 4, 2
        for msg in msgs:
            self.screen.move(x, y)
            self.screen.clrtoeol()
            self.screen.addstr(x, y, msg["time"], curses.color_pair(1))
            self.screen.addstr(x, y+9, msg["score"], curses.color_pair(1))
            self.screen.addstr(x, y+18, msg["team"], curses.color_pair(1))
            self.screen.addstr(x, y+24, msg["info"], curses.color_pair(1))
            x += 1
            y = 2
        self.screen.refresh()

    def exit():
        curses.nocbreak();
        self.screen.keypad(0);
        curses.echo()
        
