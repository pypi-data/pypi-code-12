def main():
	import optparse
	import functions
	p = optparse.OptionParser()
	p.add_option('--user', '-u', default="arslancb")
	p.add_option('--download', '-d', default="/var/www/html")
	options, arguments = p.parse_args()

	if options.user:
		downloadLocation = options.download
		user = options.user
		allAcounts = [user]
		for theuser in allAcounts:
			print "Fetching " + theuser
			landPage = functions.initPageData(theuser)
			cleaned = functions.cleanData(landPage,downloadLocation)

if __name__ == '__main__':
    main()