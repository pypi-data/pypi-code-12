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

from examples.docs import fixtures
from facebookads import test_config

ad_account_id = test_config.account_id
page_id = test_config.page_id
sponsor_page_id = test_config.secondary_page_id
image_hash = fixtures.create_image().get_hash()
link = 'http://example.com'

# _DOC oncall [clu]
# _DOC open [ADCREATIVE_CREATE_PHOTO_BRANDED_AD]
# _DOC vars [ad_account_id:s, image_hash:s, page_id, link:s, sponsor_page_id]
from facebookads.objects import AdCreative
from facebookads.specs import ObjectStorySpec, PhotoData

photo_data = PhotoData()
photo_data[PhotoData.Field.caption] = 'My caption'
photo_data[PhotoData.Field.image_hash] = image_hash
photo_data[PhotoData.Field.branded_content_sponsor_page_id] = sponsor_page_id

object_story_spec = ObjectStorySpec()
object_story_spec[ObjectStorySpec.Field.page_id] = page_id
object_story_spec[ObjectStorySpec.Field.photo_data] = photo_data

creative = AdCreative(parent_id=ad_account_id)
creative[AdCreative.Field.name] = 'AdCreative for Branded Content Sponsor Ad'
creative[AdCreative.Field.object_story_spec] = object_story_spec
creative.remote_create()

print(creative)
# _DOC close [ADCREATIVE_CREATE_PHOTO_BRANDED_AD]

creative.remote_delete()
