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

ad_account_id = test_config.account_id

# _DOC open [ADACCOUNT_GET_INSIGHTS_CAROUSEL_BREAKDOWNS]
# _DOC vars [ad_account_id:s]
from facebookads.objects import AdAccount, Insights

account = AdAccount(ad_account_id)

params = {
    'action_breakdowns': [
        Insights.ActionBreakdown.action_type,
        Insights.ActionBreakdown.action_carousel_card_id,
    ],
    'fields': [
        Insights.Field.impressions,
        Insights.Field.unique_clicks,
        Insights.Field.actions,
        Insights.Field.website_ctr,
    ],
    'level': Insights.Level.ad,
    'date_preset': Insights.Preset.last_30_days,
    'time_increment': 'all_days',
    'breakdowns': Insights.Breakdown.placement,
    'filtering': [{
        'field': 'action_type',
        'operator': 'IN',
        'value': ['link_click']
    }]
}

stats = account.get_insights(params=params)
print(stats)
# _DOC close [ADACCOUNT_GET_INSIGHTS_CAROUSEL_BREAKDOWNS]
