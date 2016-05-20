from os.path import abspath
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from contextlib import contextmanager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import \
    visibility_of as visible, staleness_of

from locators import RecordingsLocators, \
                     UploadLocators, \
                     TrimLocators, \
                     LoginLocators, \
                     AdminLocators


class BasePage(object):

    def __init__(self, browser):
        self.browser = browser

    def reload(self):
        self.browser.reload()

    def default_frame(self):
        self.driver.switch_to.default_content()

    def js(self, *args):
        self.browser.execute_script(*args)

    @contextmanager
    def switch_frame(self, iframe):
        self.browser.driver.switch_to.frame(iframe._element)
        yield
        self.browser.driver.switch_to.default_content()

    def clear(self, elem):
        elem._element.clear()

    def get_element(self, locator):
        return self.get_elements(locator).first

    def get_elements(self, locator):
        get_by, selector = locator
        if get_by == By.CSS_SELECTOR:
            return self.browser.find_by_css(selector)
        elif get_by == By.NAME:
            return self.browser.find_by_name(selector)
        else:
            raise NotImplementedError()

    def get_select(self, locator):
        return Select(self.get_element(locator)._element)

    @contextmanager
    def wait_for_page_change(self, tag='html', timeout=10):
        old_ref = self.browser.find_by_tag(tag)._element
        yield
        WebDriverWait(self.browser.driver, timeout) \
            .until(staleness_of(old_ref))


class ApiDocPage(BasePage):

    def __init__(self, browser, doc_page_url):
        super(ApiDocPage, self).__init__(browser)
        self.browser.visit(doc_page_url)
        # go ahead and reveal all the testing forms
        self.js("$('div.hidden_form').show()")

    def submit_form(self, form_id, data):
        for field_id, value in data.items():
            sel = "#%s #%s" % (form_id, field_id)
            elem = self.browser.find_by_css(sel).first
            elem.fill(value)
        form = self.get_element((By.CSS_SELECTOR, "#%s" % form_id))
        # drop down to selenium for convenience
        form._element.submit()


class LoginPage(BasePage):

    @property
    def username_input(self):
        return self.get_element(LoginLocators.USERNAME_INPUT)

    @property
    def password_input(self):
        return self.get_element(LoginLocators.PASSWORD_INPUT)

    @property
    def submit(self):
        return self.get_element(LoginLocators.SUBMIT_BUTTON)

    def login(self, username, password):
        self.username_input.type(username)
        self.password_input.type(password)
        self.submit.click()


class AdminPage(BasePage):

    @property
    def recordings_tab(self):
        return self.get_element(AdminLocators.RECORDINGS_TAB)


class RecordingsPage(AdminPage):

    @property
    def upload_recording_button(self):
        return self.get_element(RecordingsLocators.UPLOAD_RECORDING_BUTTON)

    @property
    def search_select(self):
        return self.get_select(RecordingsLocators.SEARCH_SELECT)

    @property
    def search_input(self):
        return self.get_element(RecordingsLocators.SEARCH_INPUT)

    @property
    def per_page_select(self):
        return self.get_select(RecordingsLocators.PERPAGE_SELECT)

    @property
    def refresh_checkbox(self):
        return self.get_element(RecordingsLocators.REFRESH_CHECKBOX)

    @property
    def on_hold_tab(self):
        return self.get_element(RecordingsLocators.ON_HOLD_TAB)

    @property
    def trim_links(self):
        return self.get_elements(RecordingsLocators.TRIM_LINK)

    def refresh_off(self):
        self.refresh_checkbox.uncheck()
        self.js('window.clearInterval(ocRecordings.refreshInterval);')

    def filter_recordings(self, field, value):
        self.search_select.select_by_value(field)
        self.search_input.type(value)
        self.search_input.type(Keys.RETURN)
        found = self.get_element(RecordingsLocators.FILTER_FOUND_COUNT)
        return found

    def max_per_page(self):
        self.per_page_select.select_by_visible_text('100')

    def switch_to_tab(self, tab_elem):
        """
        bypass the usual element click() method as these tab links frequently
        throw exceptions about not being clickable at point blah, blah
        """
        self.browser.driver.execute_script("arguments[0].click();", tab_elem)


class UploadPage(BasePage):

    @property
    def title_input(self):
        return self.get_element(UploadLocators.TITLE_INPUT)

    @property
    def presenter_input(self):
        return self.get_element(UploadLocators.PRESENTER_INPUT)

    @property
    def series_input(self):
        return self.get_element(UploadLocators.SERIES_INPUT)

    @property
    def series_filter(self):
        return self.get_element(UploadLocators.SERIES_FILTER)

    @property
    def series_autocomplete_items(self):
        return self.get_elements(UploadLocators.SERIES_AUTOCOMPLETE_ITEM)

    @property
    def course_input(self):
        return self.get_element(UploadLocators.COURSE_INPUT)

    @property
    def license_select(self):
        return self.get_select(UploadLocators.LICENSE_SELECT)

    @property
    def rec_date_input(self):
        return self.get_element(UploadLocators.REC_DATE_INPUT)

    @property
    def start_hour_select(self):
        return self.get_select(UploadLocators.START_HOUR_SELECT)

    @property
    def start_minute_select(self):
        return self.get_select(UploadLocators.START_MINUTE_SELECT)

    @property
    def contributor_input(self):
        return self.get_element(UploadLocators.CONTRIBUTOR_INPUT)

    @property
    def type_input(self):
        return self.get_element(UploadLocators.TYPE_INPUT)

    @property
    def subject_input(self):
        return self.get_element(UploadLocators.SUBJECT_INPUT)

    @property
    def lang_input(self):
        return self.get_element(UploadLocators.LANG_INPUT)

    @property
    def desc_input(self):
        return self.get_element(UploadLocators.DESC_INPUT)

    @property
    def copyright_input(self):
        return self.get_element(UploadLocators.COPYRIGHT_INPUT)

    @property
    def single_file_radio(self):
        return self.get_element(UploadLocators.SINGLE_FILE_RADIO)

    @property
    def multi_file_radio(self):
        return self.get_element(UploadLocators.MULTI_FILE_RADIO)

    @property
    def single_file_local_radio(self):
        return self.get_element(UploadLocators.SINGLE_FILE_LOCAL_RADIO)

    @property
    def single_file_inbox_radio(self):
        return self.get_element(UploadLocators.SINGLE_FILE_INBOX_RADIO)

    @property
    def multi_file_presentation_local_radio(self):
        return self.get_element(UploadLocators.MULTI_FILE_PRESENTATION_LOCAL_RADIO)

    @property
    def multi_file_presenter_local_radio(self):
        return self.get_element(UploadLocators.MULTI_FILE_PRESENTER_LOCAL_RADIO)

    @property
    def multi_file_presentation_inbox_radio(self):
        return self.get_element(UploadLocators.MULTI_FILE_PRESENTATION_INBOX_RADIO)

    @property
    def multi_file_presenter_inbox_radio(self):
        return self.get_element(UploadLocators.MULTI_FILE_PRESENTER_INBOX_RADIO)

    @property
    def file_input_iframes(self):
        return self.get_elements(UploadLocators.FILE_INPUT_IFRAME)

    @property
    def local_file_selector(self):
        return self.get_element(UploadLocators.LOCAL_FILE_SELECTOR)

    @property
    def inbox_file_select(self):
        return self.get_select(UploadLocators.INBOX_FILE_SELECT)

    @property
    def contains_slides_checkbox(self):
        return self.get_element(UploadLocators.CONTAINS_SLIDES_CHECKBOX)

    @property
    def workflow_select(self):
        return self.get_select(UploadLocators.WORKFLOW_SELECT)

    @property
    def live_stream_checkbox(self):
        return self.get_element(UploadLocators.LIVE_STREAM_CHECKBOX)

    @property
    def multitrack_checkbox(self):
        return self.get_element(UploadLocators.MULTITRACK_CHECKBOX)

    @property
    def upload_button(self):
        return self.get_element(UploadLocators.UPLOAD_BUTTON)

    @property
    def upload_progress_dialog(self):
        return self.get_element(UploadLocators.UPLOAD_PROGRESS_DIALOG)

    def set_series(self, series):
        self.clear(self.series_filter)
        self.series_input.type(series)
        self.series_autocomplete_items[0].click()

    def set_upload_files(self, presenter=None, presentation=None,
                         combined=None, is_inbox=False):
        """
        The MH upload UI does some crazy stuff with iframes.
        None of the iframe elements have unique ids, so this
        and the subsequent _private methods have to make some
        assumptions about the order in which they are returned
        by the locator elements.
        """
        if combined is not None:
            self.single_file_radio.click()
            if is_inbox:
                self.single_file_inbox_radio.click()
            else:
                self.single_file_local_radio.click()
            self.set_upload_file(0, combined, is_inbox)
        else:
            self.multi_file_radio.click()
            if is_inbox:
                self.multi_file_presentation_inbox_radio.click()
                self.multi_file_presenter_inbox_radio.click()
            else:
                self.multi_file_presentation_local_radio.click()
                self.multi_file_presenter_local_radio.click()
            self.set_upload_file(1, presentation, is_inbox)
            self.set_upload_file(2, presenter, is_inbox)

    def set_upload_file(self, iframe_idx, file, is_inbox):
        iframe = self.file_input_iframes[iframe_idx]
        with self.switch_frame(iframe):
            if is_inbox:
                self.inbox_file_select.select_by_value(file)
            else:
                # NOTE: this will silently fail if it's not
                # an absolute path to an existing file
                self.local_file_selector.fill(abspath(file))

    def wait_for_upload_finish(self):
        WebDriverWait(self.browser.driver, 1000000) \
            .until_not(visible(self.upload_progress_dialog._element))


class TrimPage(BasePage):

    @property
    def trim_iframe(self):
        return self.get_element(RecordingsLocators.TRIM_IFRAME)

    @property
    def shortcut_table(self):
        return self.get_element(TrimLocators.SHORTCUT_TABLE)

    @property
    def trim_begin_input(self):
        return self.get_element(TrimLocators.CLIP_BEGIN_INPUT)

    @property
    def trim_end_input(self):
        return self.get_element(TrimLocators.CLIP_END_INPUT)

    @property
    def trim_ok_button(self):
        return self.get_element(TrimLocators.CLIP_OK_BUTTON)

    @property
    def split_remover(self):
        return self.get_element(TrimLocators.CLIP_REMOVE_BUTTON)

    @property
    def continue_button(self):
        return self.get_element(TrimLocators.CONTINUE_BUTTON)

    @property
    def clear_button(self):
        return self.get_element(TrimLocators.CLEAR_BUTTON)

    def trim(self):
        self.clear_button.click()
        sleep(1)

        # safe to assume media is > 10 seconds?
        self.shortcut_table.type("l" * 20)
        sleep(1)
        self.shortcut_table.type("v")
        sleep(1)
        self.shortcut_table.type(Keys.ARROW_UP)
        sleep(1)
        self.shortcut_table.type(Keys.DELETE)
        sleep(1)

        # media_length = timeparse(self.trim_end_input.get_attribute('value'))
        # trim_length = media_length / 10
        # self.trim_begin_input.clear()
        # self.trim_begin_input.send_keys(str(datetime.timedelta(seconds=trim_length)))
        # self.trim_ok_button.click()
        # sleep(2)
        # self.split_remover.click()

        self.continue_button.click()
        sleep(2)
