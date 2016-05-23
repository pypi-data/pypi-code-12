
class Athletelist(list):
    def __init__(self,a_name,a_dob = None,a_times = []):
        self.name = a_name
        self.dob = a_dob
        self.times = a_times

    ##Get the top 3 fastest times    
    def top3(self):
        def sanitize(time_string):
            ##Replace the '-' and ':' with '.'
            return time_string.replace('-','.').replace(':','.')
        return sorted(set(sanitize(t) for t in self.times))[0:3] 
