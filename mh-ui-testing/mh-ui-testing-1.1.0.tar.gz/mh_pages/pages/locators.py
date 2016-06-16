from selenium.webdriver.common.by import By


class LoginLocators(object):
    USERNAME_INPUT = (By.NAME, 'j_username')
    PASSWORD_INPUT = (By.NAME, 'j_password')
    SUBMIT_BUTTON = (By.NAME, 'submit')


class AdminLocators(object):
    RECORDINGS_TAB = (By.CSS_SELECTOR, 'a#i18n_tab_recording')


class RecordingsLocators(object):
    UPLOAD_RECORDING_BUTTON = (By.CSS_SELECTOR, 'button#uploadButton')
    SEARCH_SELECT = (By.CSS_SELECTOR, 'div#searchBox > select')
    SEARCH_INPUT = (By.CSS_SELECTOR, 'div#searchBox > span > input')
    FILTER_FOUND_COUNT = (By.CSS_SELECTOR, 'span#filterRecordingCount')
    PERPAGE_SELECT = (By.CSS_SELECTOR, 'select#pageSize')
    REFRESH_CHECKBOX = (By.CSS_SELECTOR, 'input#refreshEnabled')
    ON_HOLD_TAB = (By.CSS_SELECTOR, 'label[for=state-hold]')
    TRIM_LINK = (By.CSS_SELECTOR, 'a[title="Review / VideoEdit"]')
    TRIM_IFRAME = (By.CSS_SELECTOR, 'iframe#holdActionUI')


class UploadLocators(object):
    TITLE_INPUT = (By.CSS_SELECTOR, 'input#title')
    PRESENTER_INPUT = (By.CSS_SELECTOR, 'input#creator')
    SERIES_INPUT = (By.CSS_SELECTOR, 'input#seriesSelect')
    SERIES_FILTER = (By.CSS_SELECTOR, 'input#dceTermFilter')
    SERIES_AUTOCOMPLETE_ITEM = (By.CSS_SELECTOR, 'ul.ui-autocomplete a')
    COURSE_INPUT = (By.CSS_SELECTOR, 'input#seriesSelect')
    LICENSE_SELECT = (By.CSS_SELECTOR, 'select#licenseField')
    REC_DATE_INPUT = (By.CSS_SELECTOR, 'input#recordDate')
    START_HOUR_SELECT = (By.CSS_SELECTOR, 'select#startTimeHour')
    START_MINUTE_SELECT = (By.CSS_SELECTOR, 'select#startTimeMin')
    CONTRIBUTOR_INPUT = (By.CSS_SELECTOR, 'input#contributor')
    TYPE_INPUT = (By.CSS_SELECTOR, 'input#type')
    SUBJECT_INPUT = (By.CSS_SELECTOR, 'input#subject')
    LANG_INPUT = (By.CSS_SELECTOR, 'input#language')
    DESC_INPUT = (By.CSS_SELECTOR, 'input#description')
    COPYRIGHT_INPUT = (By.CSS_SELECTOR, 'input#copyright')

    MULTI_FILE_RADIO = (By.CSS_SELECTOR, 'input#multiUploadRadio')
    SINGLE_FILE_RADIO = (By.CSS_SELECTOR, 'input#singleUploadRadio')

    FILE_INPUT_IFRAME = (By.CSS_SELECTOR, 'iframe.uploadForm-container')

    SINGLE_FILE_LOCAL_RADIO = (By.CSS_SELECTOR, 'input#fileSourceSingleA')
    SINGLE_FILE_INBOX_RADIO = (By.CSS_SELECTOR, 'input#fileSourceSingleB')

    MULTI_FILE_PRESENTATION_LOCAL_RADIO = (By.CSS_SELECTOR,
                                           'input#fileSourcePresentationA')
    MULTI_FILE_PRESENTATION_INBOX_RADIO = (By.CSS_SELECTOR,
                                           'input#fileSourcePresentationB')
    MULTI_FILE_PRESENTER_LOCAL_RADIO = (By.CSS_SELECTOR,
                                        'input#fileSourcePresenterA')
    MULTI_FILE_PRESENTER_INBOX_RADIO = (By.CSS_SELECTOR,
                                        'input#fileSourcePresenterB')

    LOCAL_FILE_SELECTOR = (By.CSS_SELECTOR, 'input#file')
    INBOX_FILE_SELECT = (By.CSS_SELECTOR, 'select#file')

    CONTAINS_SLIDES_CHECKBOX = (By.CSS_SELECTOR, 'input#containsSlides')
    WORKFLOW_SELECT = (By.CSS_SELECTOR, 'select#workflowSelector')
    LIVE_STREAM_CHECKBOX = (By.CSS_SELECTOR, 'input#hasLive')
    MULTITRACK_CHECKBOX = (By.CSS_SELECTOR, 'input#epiphanUpload')
    UPLOAD_BUTTON = (By.CSS_SELECTOR, 'button#submitButton')
    UPLOAD_PROGRESS_DIALOG = (By.CSS_SELECTOR, 'div#progressStage')


class TrimLocators(object):
    SHORTCUT_TABLE = (By.CSS_SELECTOR, 'div#rightBox')
    CLIP_BEGIN_INPUT = (By.CSS_SELECTOR, 'span#clipBegin > input')
    CLIP_END_INPUT = (By.CSS_SELECTOR, 'span#clipEnd > input')
    CLIP_OK_BUTTON = (By.CSS_SELECTOR, 'input#okButton')
    CLIP_REMOVE_BUTTON = (By.CSS_SELECTOR, 'a#splitRemover-0')
    CONTINUE_BUTTON = (By.CSS_SELECTOR, 'input#continueButton')
    CLEAR_BUTTON = (By.CSS_SELECTOR, 'input#clearList')
