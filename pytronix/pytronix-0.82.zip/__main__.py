from pytronix import scrape, serve
import sys

if len(sys.argv) > 1:
	scrape(sys.argv[1])
else:
	serve()

