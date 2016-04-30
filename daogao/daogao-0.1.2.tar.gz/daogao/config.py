default_config = """
[server]
listen = 8081
max_threads = 5

[delivery]
url_base = http://localhost

[mailgun]
; api_key = abc123
; domain_name = foo.com
; from = postmaster@foo.com
"""

if __name__ == '__main__':
	import sys
	params = sys.argv[1:]
	lparam = len(params)
	if lparam < 0:
		sys.exit(1)

	op = params[0]
	
	if op == 'default':
		print(default_config)