# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.firefox.base import FirefoxBasePage


class FirefoxWhatsNewNightly70Page(FirefoxBasePage):

    URL_TEMPLATE = '/{locale}/firefox/70.0a1/whatsnew/all/'

    _upgrade_message_locator = (By.CSS_SELECTOR, '.main-content header > h2')

    @property
    def is_upgrade_message_displayed(self):
        return self.is_element_displayed(*self._upgrade_message_locator)
