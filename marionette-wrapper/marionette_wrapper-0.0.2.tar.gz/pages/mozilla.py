# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette_driver import By

from base import Base


class Mozilla(Base):
    _mozilla_tabzilla_div_locator = (By.ID, 'tabzilla')

    def __init__(self, marionette, url=None):
        super(Mozilla, self).__init__(marionette)
        self.launch(url)
        self.wait_for_element_displayed(*self._mozilla_tabzilla_div_locator)
