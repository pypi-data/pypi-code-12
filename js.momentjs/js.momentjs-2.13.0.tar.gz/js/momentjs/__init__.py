from fanstatic import Library, Resource

library = Library('moment.js', 'resources')

moment = Resource(library, 'moment.js', minified='moment.min.js')

moment_timezone = Resource(
    library, 'moment-timezone.js',
    minified='moment-timezone.min.js',
    depends=[moment])

moment_timezone_with_data = Resource(
    library, 'moment-timezone-with-data.js',
    minified='moment-timezone-with-data.min.js',
    depends=[moment])

moment_with_locales = Resource(
    library,
    'moment-with-locales.js',
    minified='moment-with-locales.min.js')

locales = {
    'nl': Resource(library, 'locale/nl.js', depends=[moment]),
    'de': Resource(library, 'locale/de.js', depends=[moment]),
    'es': Resource(library, 'locale/es.js', depends=[moment]),
}
