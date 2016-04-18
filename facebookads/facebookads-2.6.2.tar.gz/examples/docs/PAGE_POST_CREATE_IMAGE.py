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

from facebookads import test_config, FacebookAdsApi
from examples.docs import fixtures
from facebookads.objects import AdImage

page_id = test_config.page_id
link = test_config.app_url
image_url = fixtures.create_image()[AdImage.Field.url]
FacebookAdsApi.set_default_api(fixtures.get_page_api())

# _DOC oncall [yinshiz]
# _DOC open [PAGE_POST_CREATE_IMAGE]
# _DOC vars [page_id, image_url:s, link:s]
from facebookads import FacebookAdsApi

params = {
    'massage': 'Sign up today.',
    'picture': image_url,
    'link': link,
    'published': 1,
    'call_to_action': {
        'type': 'SIGN_UP',
        'value': {
            'link': link,
        },
    },
}

data = FacebookAdsApi.get_default_api().\
    call('POST', (page_id, 'feed'), params=params)
# _DOC close [PAGE_POST_CREATE_IMAGE]

FacebookAdsApi.get_default_api().\
    call('DELETE', (data.json()['id'],))
