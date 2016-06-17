import inspect

# Constants
DEFAULT_DELTA = 1e-6
COLORS = {
	"red":   "\033[91m",
	"green": "\033[92m",
	"bold":  "\033[1m",
	"reset": "\033[0m"
}

# Global variables
total = 0
passed = 0

# Utils
def within(actual, expected, tolerance=DEFAULT_DELTA):
    """
    Real Real [Real] -> bool

    Returns true if the given numbers are within `tolerance` of
    each other.
    """
    return abs(actual - expected) <= tolerance

def expect(actual, expected):
	global total, passed
	if not compare(actual, expected):
		curr = inspect.currentframe()
		caller = inspect.getouterframes(curr)[1]
		line = str(caller[2])
		code = caller[4]
		print(
			COLORS["red"] + "Test failed:" + COLORS["reset"] +
			" expected " + str(expected) + " but got " + str(actual))
		print(
			" " * (6 - len(line)) +
			COLORS["bold"] + "Line " + line + ": " + COLORS["reset"] +
			code[0].strip() +
			("..." if len(code) > 1 else "")
		)
	else:
		passed += 1
	total += 1

def compare(a, b):
	if (type(a) is float or type(b) is float):
		return within(a, b)
	else:
		return a == b

def summary():
	color = COLORS["green"] if (total == passed) else COLORS["red"]
	print(color + str(passed) + " of " + str(total) + " tests passed" + COLORS["reset"])
	reset()

def reset():
    global total, passed
    passed = 0
    total = 0

def start_testing():
    reset()
