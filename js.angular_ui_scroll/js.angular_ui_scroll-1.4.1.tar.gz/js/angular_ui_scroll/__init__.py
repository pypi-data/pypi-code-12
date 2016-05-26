from fanstatic import Library, Resource
import js.angular
import js.jquery

library = Library('angular_ui_scroll', 'resources')

ui_scroll = Resource(
    library, 'ui-scroll.js', minified='ui-scroll.min.js',
    depends=[js.angular.angular, js.jquery.jquery])
