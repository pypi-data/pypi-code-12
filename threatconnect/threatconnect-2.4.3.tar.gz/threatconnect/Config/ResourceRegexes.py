""" standard """
import re

# api version
api_version = 'v2'

#
# address indicator (ipv4/ipv6 regex)
#
ipv4_pat = r'\.'.join([r'(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])'] * 4)
ipv4_re = re.compile(ipv4_pat + '$')
ipv6_re = re.compile(
    '(?:%(hex4)s:){6}%(ls32)s$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$'
    '|::(?:%(hex4)s:){5}%(ls32)s$'
    '|(?:%(hex4)s)?::(?:%(hex4)s:){4}%(ls32)s$'
    '|(?:(?:%(hex4)s:)?%(hex4)s)?::(?:%(hex4)s:){3}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,2}%(hex4)s)?::(?:%(hex4)s:){2}%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,3}%(hex4)s)?::%(hex4)s:%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,4}%(hex4)s)?::%(ls32)s$'
    '|(?:(?:%(hex4)s:){0,5}%(hex4)s)?::%(hex4)s$'
    '|(?:(?:%(hex4)s:){0,6}%(hex4)s)?::$' % {
        'ls32': r'(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|%s)' % ipv4_pat,
        'hex4': r'[0-9a-f]{1,4}'}, re.IGNORECASE)

#
# emailAddress indicator
#
# email_pat = r'[^@]+@[^@]+\.[^@]+$'
# email_re = re.compile(email_pat)
email_re = re.compile(
    '[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/='
    '?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+'
    '[a-z0-9](?:[a-z0-9-]*[a-z0-9])?')

#
# md5/sha256 indicator
#
md5_pat = r'^([a-fA-F\d]{32})$'
md5_re = re.compile(md5_pat)
sha1_pat = r'^([a-fA-F\d]{40})$'
sha1_re = re.compile(sha1_pat)
sha256_pat = r'^([a-fA-F\d]{64})$'
sha256_re = re.compile(sha256_pat)

#
# host indicator
#
# host_pat = r'\b(([a-zA-Z0-9\-_]+)\.)+(?!exe|php|dll|doc|docx|txt|'
# host_pat += r'rtf|odt|xls|xlsx|ppt|pptx|bin|pcap|ioc|pdf|mdb|asp|html'
# host_pat += r'|xml|jpg|gif|png|lnk|log|vbs|lco|bat|shell|quit|pdb|vbp'
# host_pat += r'|bdoda|bsspx|save|cpl|wav|tmp|close|py|ico|ini|sleep|run'
# host_pat += r'|dat|scr|jar|jxr|apt|w32|css|js|xpi|class|apk|rar|zip|hlp'
# host_pat += r'|tmp|cpp|crl|cfg|cer|plg|tmp)(support|report|i2p|technology'
# host_pat += r'|xn--p1ai|com|moscow|technology)\b'
# host_re = re.compile(host_pat)

host_pat = r'\b(([a-zA-Z0-9\-_]+)\.)+(?!exe|php|dll|doc|docx|txt'
host_pat += r'|rtf|odt|xls|xlsx|ppt|pptx|bin|pcap|ioc|pdf|mdb|asp|html'
host_pat += r'|xml|jpg|gif|png|lnk|log|vbs|lco|bat|shell|quit|pdb|vbp'
host_pat += r'|bdoda|bsspx|save|cpl|wav|tmp|close|py|ico|ini|sleep|run'
host_pat += r'|dat|scr|jar|jxr|apt|w32|css|js|xpi|class|apk|rar|zip|hlp'
host_pat += r'|tmp|cpp|crl|cfg|cer|plg|tmp)([a-zA-Z]{2,5}|support|report'
host_pat += r'|i2p|technology|xn--p1ai|com#|moscow|technology)'
host_re = re.compile(host_pat)

#
# url indicator (this regex needs some work)
#
url_pat = r"""\b(https?|sftp|ftp|file)://[-a-zA-Z0-9+&@#/%?=~_|!:,.;'"*$()]*[a-zA-Z0-9+&@#/%=~_|]"""
url_re = re.compile(url_pat)

indicators_regex = {
    'ADDRESSES': [ipv4_re, ipv6_re],
    'EMAIL_ADDRESSES': [email_re],
    'FILES': [md5_re, sha1_re, sha256_re],
    'HOSTS': [host_re],
    'URLS': [url_re]}
