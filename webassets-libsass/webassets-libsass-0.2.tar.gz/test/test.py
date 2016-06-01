from webassets import Environment, Bundle

from webassets.filter import register_filter
from webassets_libsass import LibSass

register_filter(LibSass)

asset_env = Environment(
    directory='css',
    url='css',
)
asset_env.debug = False
asset_env.url_expire = False
asset_env.config['LIBSASS_OUTPUT_STYLE'] = 'compressed'


# CSS/SCSS #
# vars
scss_dir = '../scss'

# widgets
libsass_test = Bundle(scss_dir + '/test.scss', filters='libsass', output='test.css')
asset_env.register('test', libsass_test)
print(asset_env['test'].urls())
