class logger:
    END = '\033[0m'

    formats = {
        'b':'\033[1m',            # bold
        'u':'\033[4m',            # underline
        'n':''                    # none
    }

    colors = {
        'r':'\033[31m',           # red
        'g':'\033[32m',           # green
        'y':'\033[33m',           # yellow
        'b':'\033[34m',           # blue
        'p':'\033[35m',           # purple
        'c':'\033[36m',           # cyan
        'n':''                    # none
    }

    highlight_colors = {
        'r':'\033[41m',           # red
        'g':'\033[42m',           # green
        'y':'\033[43m',           # yellow
        'b':'\033[44m',           # blue
        'p':'\033[45m',           # purple
        'c':'\033[46m',           # cyan
        'n':''                    # none
    }

    @classmethod
    def log(c, s, color='n', highlight='n', format='n'):
        print c.colors[color] + c.highlight_colors[highlight] + c.formats[format] + s + c.END
