DEFAULT_NGINX = {
    'dir_path': '/var/log/nginx/',
    'accesslog_filename': 'access.log',
    'errorlog_filename': 'error.log',
    'dateminutes_format': '[%d/%b/%Y:%H:%M',
    'datehours_format': '[%d/%b/%Y:%H',
    'datedays_format': '[%d/%b/%Y',
    'request_model': (r''
                      '(\d+.\d+.\d+.\d+)\s-\s-\s'
                      '\[(.+)\]\s'
                      '(?i)"?(GET|POST|PUT|HEAD|DELETE|OPTIONS|CONNECT|PATCH)\s(.+)\s\w+/.+"'
                      '\s(\d+)\s'
                      '\d+\s"(.+)"\s'
                      '"(.+)"')
}


DEFAULT_APACHE2 = {
    'dir_path': '/var/log/apache2/',
    'accesslog_filename': 'access.log',
    'errorlog_filename': 'error.log',
    'dateminutes_format': '[%d/%b/%Y:%H:%M',
    'datehours_format': '[%d/%b/%Y:%H',
    'datedays_format': '[%d/%b/%Y',
    'request_model': (r''
                      '(\d+.\d+.\d+.\d+)\s-\s-\s'
                      '\[(.+)\]\s'
                      '(?i)"?(\w+)\s(.+)\s\w+/.+"'
                      '\s(\d+)\s'
                      '\d+\s"(.+)"\s'
                      '"(.+)"')
}


DEFAULT_AUTH = {
    'dir_path': '/var/log/',
    'accesslog_filename': 'auth.log',
    'dateminutes_format': '%b %e %H:%M:',
    'datehours_format': '%b %e %H:',
    'datedays_format': '%b %e ',
    'request_model': (r''
                      '(\w+\s\s\d+\s\d+:\d+:\d+)\s'
                      '\w+\s(\w+)\[\d+\]:\s'
                      '(.+)')
}


SERVICES_SWITCHER = {
    'nginx': DEFAULT_NGINX,
    'apache2': DEFAULT_APACHE2,
    'auth': DEFAULT_AUTH
}

IPv4_REGEX = r'(\d+.\d+.\d+.\d+)'
AUTH_USER_INVALID_USER = r'(?i)invalid\suser\s(\w+)\s'
AUTH_PASS_INVALID_USER = r'(?i)failed\spassword\sfor\s(\w+)\s'
