from fanstatic import Library, Resource, Group

library = Library('video.js', 'resources')

# By default, we bundle Video.js with Mozilla's excellent VTT.js.
videojs_js = Resource(
    library, 'video.js', minified='video.min.js')

# If you don't need VTT.js functionality for whatever reason, you can use one
# of the Video.js copies that don't include VTT.js.
videojs_js_novtt = Resource(
    library, 'alt/video.novtt.js', minified='alt/video.novtt.min.js')

videojs_js_ie8 = Resource(
    library, 'ie8/videojs-ie8.js', minified='ie8/videojs-ie8.min.js')

videojs_css = Resource(library, 'video-js.css', minified='video-js.min.css')


def render_shockwave_url(url):
    return '''
        <script type="text/javascript">
            videojs.options.flash.swf = '%s';
        </script>''' % url

# Dependency, in order to get the path to the SWF to work.
videojs_shockwave = Resource(
    library, 'video-js.swf',
    depends=[videojs_js],
    renderer=render_shockwave_url)

videojs = Group(depends=[videojs_js, videojs_css, videojs_shockwave])

videojs_novtt = Group(
    depends=[
        videojs_js_novtt,
        videojs_css,
        videojs_shockwave])

videojs_ie8 = Group(
    depends=[
        videojs_js_ie8,
        videojs_css,
        videojs_shockwave])
