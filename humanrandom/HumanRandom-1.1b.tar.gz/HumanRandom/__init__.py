import random
from difflib import SequenceMatcher

class HumanRandomError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

_int_history = []
_int_minmax = (0,0)

def shuffle(thelist, amt=1): # shuffle(items to shuffle[, randomness factor])
	if type(thelist) is not list:
		raise HumanRandomError("Input is not a list, cannot shuffle.")
	if type(amt) is not int and type(amt) is not float and type(amt) is not long and type(amt) is not complex:
		raise HumanRandomError("Human-ness factor is not a valid number type.")
	if len(thelist) <= 1:
		return thelist

	random.shuffle(thelist)
	for h in range(0,int(amt)):
		i = 0
		while i < len(thelist):
			if (SequenceMatcher(None, str(thelist[i]), str(thelist[i-1])).ratio() * amt) > 0.5:
				thelist.insert(-1, thelist.pop(i))
			i += 1
	return thelist

def randint(min, max, amt=1): # randint(minimum value, maximum value[, randomness factor])
	global _int_history
	global _int_minmax

	if type(min) is not int or type(max) is not int:
		raise HumanRandomError("Min or max is not an integer.")
	if type(amt) is not int and type(amt) is not float and type(amt) is not long and type(amt) is not complex:
		raise HumanRandomError("Human-ness factor is not a valid number type.")

	if min != _int_minmax[0] or max != _int_minmax[1]:
		_int_minmax = (min,max)
		_int_history = []
	if len(_int_history) < 1:
		_int_history.append(random.randint(min,max))
		return _int_history[-1]
	j = random.randint(min,max)
	while (_int_history[-1] - (float(amt)/(max-min))) < j < (_int_history[-1] + (float(amt)/(max-min))):
		j = random.randint(min,max)
	_int_history.append(j)
	return j
