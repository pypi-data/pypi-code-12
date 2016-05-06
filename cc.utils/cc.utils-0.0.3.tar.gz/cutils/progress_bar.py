import sys
from random import uniform


class ProgressBar:
    def __init__(self, total=0, start_count=0, width=50, hspace=1):
        self.count = start_count
        self.total = total
        self.width = width
        self.digit = len(str(self.total))
        self.outof = '{0:>' + str(self.digit + 1) + '} / {1:<' + str(self.digit) + '}: '
        self.hspace = hspace

    def move(self):
        self.count += 1
        return self

    def log(self, s=''):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        if s != '':
            print s
        progress = self.width * self.count / self.total
        sys.stdout.write(' ' * self.hspace + self.outof.format(self.count, self.total))
        sys.stdout.write('#' * progress + '-' * (self.width - progress))
        sys.stdout.write('  {}%'.format(round(float(self.count) / self.total * 100, 2)) + '\r')
        sys.stdout.flush()
        return self

    def skip_move(self, p_skip=0.8):
        self.move()
        if uniform(0, 1) > p_skip:
            self.log()
        return self

    def close(self):
        sys.stdout.write('\n')
        sys.stdout.flush()
        return self


# import time
# bar = ProgressBar(total=1901)
# for i in range(1901):
#     bar = bar.move().log()
#     time.sleep(0.01)
# bar.close()
