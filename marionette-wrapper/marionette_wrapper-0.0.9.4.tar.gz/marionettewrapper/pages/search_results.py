# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette_driver import By

from marionettewrapper.base import Base


class SearchResults(Base):
    _search_results_search_input_box_locator = (By.ID, 'yschsp')
    _search_results_search_button_locator = (
        By.CSS_SELECTOR, 'div.search-assist-form-wrapper input.sbb')
    _search_results_mozilla_result_link_locator = (
        By.CSS_SELECTOR, 'ol li.first div div.layoutCenter div.compTitle h3 a')

    def __init__(self, marionette, queried_search, url=None):
        super(SearchResults, self).__init__(marionette)
        self.launch(url)
        self.wait_for_element_displayed(
            *self._search_results_search_input_box_locator)
        assert self.get_attribute(
            *self._search_results_search_input_box_locator,
            attribute='value') == queried_search

    def click_first_result_mozilla(self):
        self.wait_for_element_displayed(
            *self._search_results_mozilla_result_link_locator)
        self.click_element(*self._search_results_mozilla_result_link_locator)
        from marionettewrapper.pages import Mozilla
        self.marionette.switch_to_window(self.marionette.window_handles[1])
        return Mozilla(self.marionette)
