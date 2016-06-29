# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette_driver import By

from marionettewrapper.base import Base


class Yahoo(Base):
    _yahoo_search_input_box_locator = (By.ID, 'uh-search-box')
    _yahoo_search_button_locator = (By.ID, 'uh-search-button')
    _yahoo_search_mozilla_result_link_locator = (
        By.CSS_SELECTOR, 'ol li.first div div.layoutCenter div.compTitle h3 a')

    def __init__(self, marionette, url):
        super(Yahoo, self).__init__(marionette)
        self.launch(url)
        self.wait_for_element_displayed(*self._yahoo_search_input_box_locator)

    def search_for_query(self, query_string):
        self.send_keys_to_element(
            *self._yahoo_search_input_box_locator, string=query_string)
        self.click_element(*self._yahoo_search_button_locator)
        from marionettewrapper.pages import SearchResults
        return SearchResults(self.marionette, query_string)
