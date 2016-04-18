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
url = test_config.app_url
image_hash = fixtures.create_image().get_hash()
form_id = fixtures.get_leadgen_form().get_id()

# _DOC oncall [clu]
# _DOC open [ADCREATIVE_CREATE_CAROUSEL_LEAD_AD]
# _DOC vars [ad_account_id:s, page_id, url:s, image_hash:s, form_id]
from facebookads.objects import AdCreative
from facebookads.specs import ObjectStorySpec, LinkData, AttachmentData

child_attachments = list()
for i in range(3):
    child_attachment = AttachmentData()
    child_attachment[AttachmentData.Field.link] = url
    child_attachment[AttachmentData.Field.image_hash] = image_hash
    child_attachment[AttachmentData.Field.call_to_action] = {
        'type': 'SIGN_UP',
        'value': {
            'lead_gen_form_id': form_id,
        },
    }
    child_attachments.append(child_attachment)

link_data = LinkData()
link_data[LinkData.Field.message] = 'My description'
link_data[LinkData.Field.link] = url
link_data[LinkData.Field.caption] = 'WWW.EXAMPLE.COM'
link_data[LinkData.Field.child_attachments] = child_attachments
link_data[LinkData.Field.multi_share_optimized] = True
link_data[LinkData.Field.call_to_action] = {
    'type': 'SIGN_UP',
    'value': {
        'lead_gen_form_id': form_id,
    },
}

story = ObjectStorySpec()
story[story.Field.page_id] = page_id
story[story.Field.link_data] = link_data

creative = AdCreative(parent_id=ad_account_id)
creative[AdCreative.Field.object_story_spec] = story

creative.remote_create()
# _DOC close [ADCREATIVE_CREATE_CAROUSEL_LEAD_AD]

creative.remote_delete()
