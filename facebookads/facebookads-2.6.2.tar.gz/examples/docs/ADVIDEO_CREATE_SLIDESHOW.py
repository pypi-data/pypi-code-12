# Copyright 2014 Facebook, Inc.

# You are hereby granted a non-exclusive, worldwide, royalty-free license to
# use, copy, modify, and distribute this software in source code or binary
# form for use in connection with the web services and APIs provided by
# Facebook.

# As with any software that integrates with the Facebook platform, your use
# of this software is subject to the Facebook Developer Principles and
# Policies [http://developers.facebook.com/policy/]. This copyright notice
# shall be included in all copies or substantial portions of the software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from facebookads import test_config
from examples.docs import fixtures
from facebookads.objects import AdImage

ad_account_id = test_config.account_id
image_urls = []
for i in range(0, 3):
    url = fixtures.create_image()[AdImage.Field.url]
    image_urls.append(url)

# _DOC oncall [clu]
# _DOC open [ADVIDEO_CREATE]
# _DOC vars [ad_account_id:s, image_urls]
from facebookads.objects import AdVideo
from facebookads.specs import SlideshowSpec

video = AdVideo(parent_id=ad_account_id)
slideshow = SlideshowSpec()
slideshow.update({
    SlideshowSpec.Field.images_urls: image_urls,
    SlideshowSpec.Field.duration_ms: 2000,
    SlideshowSpec.Field.transition_ms: 200,
})

video[AdVideo.Field.slideshow_spec] = slideshow
video.remote_create()
# _DOC close [ADVIDEO_CREATE]

video.remote_delete()
