"""slide2pdf is a script to convert html slide presentation to protable
document format (pdf).

Usage:
    ./slide2pdf (-u <url>) [--height=<n>] [--width=<n>]

Options:
    -h --help                show help
    -u --url URL             file-url path
    --height=<n>             window height [default: 1600]
    --width=<n>              window width [default: 1200]
"""

from docopt import docopt
from slide2pdf import slide2pdf

def main():
    args = docopt(__doc__)
    slides = slide2pdf(url=args['--url'], height=args['--height'],
                       width=args['--width'])
    slides.snap_shot()
    slides.convert_pdf()
