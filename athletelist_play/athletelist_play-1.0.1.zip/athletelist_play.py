#a test module
class Athlete(list):
    
    def __init__(self, name, dob = None, times = []):
        list.__init__(self, times)
        self.name = name
        self.dob = dob

    def top3(self):
        return sorted(set([sanitize(t) for t in self]))[0: 3]
        
def sanitize(time_string):
    if ':' in time_string:
        spliter = ':'
    elif '-' in time_string:
        spliter = '-'
    else:
        return time_string
    (fir, sec) = time_string.split(spliter)
    return fir + '.' + sec

def get_coach_data(filename):
    try:
        with open(filename) as fn:
            data = fn.readline().strip().split(',')      
        return Athlete(data.pop(0), data.pop(0), data)
    except IOError as ioerr:
        print('file open err: ' + str(ioerr))
        return Athlete(None)
