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
from facebookads.objects import Campaign

ad_account_id = test_config.account_id
params = {
    Campaign.Field.objective: Campaign.Objective.video_views,
    'status': Campaign.Status.paused,
}
campaign_id = fixtures.create_campaign(params).get_id_assured()

# _DOC oncall [yinshiz]
# _DOC open [ADSET_CREATE_CPV]
# _DOC vars [ad_account_id:s, campaign_id]
import time
from facebookads.objects import AdSet

adset = AdSet(parent_id=ad_account_id)
adset.update({
    AdSet.Field.name: 'A CPV Ad Set',
    AdSet.Field.campaign_id: campaign_id,
    AdSet.Field.daily_budget: 500,
    AdSet.Field.start_time: int(time.time()),
    AdSet.Field.end_time: int(time.time() + 100000),
    AdSet.Field.optimization_goal: AdSet.OptimizationGoal.video_views,
    AdSet.Field.billing_event: AdSet.BillingEvent.video_views,
    AdSet.Field.bid_amount: 100,
    AdSet.Field.targeting: {
        'geo_locations': {
            'countries': ['US'],
        },
        'page_types': [
            'mobilefeed',
        ],
    },
})

adset.remote_create(params={
    'status': AdSet.Status.paused,
})
# _DOC close [ADSET_CREATE_CPV]

adset.remote_delete()
