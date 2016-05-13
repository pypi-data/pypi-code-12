def get_args():
	'''Setup command line arguments

	Returns: a dict with arguments and their values
	'''
	parser = argparse.ArgumentParser(description='Crawl concordances')

	parser.add_argument("backup",
		type=filetype,
		help="""backup"""
		)

	parser.add_argument("-m", "--max-per-page",
		default=None,
		type=int,
		help="maximum number of concordances per page (default: unlimited)"
		)

	parser.add_argument("--disable-english-filter",
		default=None,
		const=True,
		action='store_const',
		help="disable filtering Non-English sentences from concordances",
		)


	filetype = argparse.FileType('w')
	parser.add_argument("-o","--output",
		default=stdout,
		type=filetype,
		help="output file (default stdout)"
		)

	parser.add_argument("-b","--bazword-generator",
		default="RANDOM",
		type=str,
		choices=["RANDOM","WIKI_ARTICLES","WIKI_TITLES","NUMBERS"],
		help="""type of bazword generator, you can choose RANDOM (random
		four-letter words), WIKI_ARTICLES (words from random articles from
		English Wikipedia), WIKI_TITLES (words from titles of random articles
		from English Wikipedia), NUMBERS (increasing numbers from 0)"""
		)

	parser.add_argument("-f","--format",
		default="json",
		type=str,
		choices=["json","xml"],
		help="output format (default %(default)s)"
		)

	parser.add_argument("-v","--verbosity",
		default=1,
		choices=[0,1,2,3],
		type=int,
		help="""Verbosity level. Every level contains also messages from higher
		levels. All this messages are printed to stderr.
		0 (DEBUG) -- logs all visiting urls before visit.
		1 (DETAILS) -- logs all crawled urls and number of found concordances.
		2 (STATUS) -- regularly logs total number of visited pages, crawled
		concordances and errors.
		3 (ERROR) -- logs just errors and anything else.
		"""
		)



def main():
	print("pokračujuL")
