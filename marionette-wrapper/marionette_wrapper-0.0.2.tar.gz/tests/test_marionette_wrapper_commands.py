# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pages.yahoo import Yahoo


class TestMarionetteWrapperCommands(object):

    def test_services_marionette_commands(self, base_url, marionette):
        yahoo_page = Yahoo(marionette, base_url)
        results_page = yahoo_page.search_for_query('Mozilla')
        mozilla_page = results_page.click_first_result_mozilla()
        mozilla_page.bookmark_page()
