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

# This file stores the information needed to perform integration testing
# on the Python Ads SDK.

import os

app_id = '131584983518288'
app_secret = '0aec118d75abc3094fffddac325082f7'
business_id = '514838258692310'
secondary_business_id = '718463758226017'
account_id = 'act_219066941615718'
secondary_account_id = 'act_434471926741884'
page_id = '360856417423829'
access_token = 'EAAB3rQQzTFABAGNThRsoRYewL2ZBHNyxS9loWJw3jPMghuo1jL8T38nDoVkL5lm3IRm2cs2f3HSCgZAtYZCoA4gYZAXOeLZCpVm016DaqN8geBVTrjZALFYEiDufTIr19tKVsM5VZArhy9FobGzpK2SLCgIR9pnYcIZD'
app_url = 'https://www.wikipedia.org'

sdk_root_dir = os.path.dirname(os.path.realpath(__file__))
test_misc_dir = os.path.join(sdk_root_dir, 'test/misc')
image_path = os.path.join(test_misc_dir, 'image.png')
images_zip_path = os.path.join(test_misc_dir, 'images.zip')
video_path = os.path.join(test_misc_dir, 'video.mp4')
