
def formatedTime(ms):
	'''
	convert milliseconds in a human readable time
	
	>>> formatedTime(60e3)
	'1m'
	>>> formatedTime(1000e3)
	'16m 40s'
	>>> formatedTime(200000123)
	'2d 7h 33m 20.123s'
	'''
	
	if ms:
		s=ms/1000.0
		m,s=divmod(s,60)
		h,m=divmod(m,60)
		d,h=divmod(h,24)
		out=''
		if d:
			out+='%gd '%d
		if h:
			out+='%gh '%h
		if m:
			out+='%gm '%m
		if s:
			out+='%gs '%s
		return out[:-1]
	return ''


if __name__ == "__main__":
	import doctest
	doctest.testmod()