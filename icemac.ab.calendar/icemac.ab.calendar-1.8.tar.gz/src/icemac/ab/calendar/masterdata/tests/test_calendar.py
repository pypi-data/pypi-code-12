from icemac.ab.calendar.interfaces import IEvent
from icemac.addressbook.interfaces import IEntity
from mechanize import LinkNotFoundError, HTTPError
import pytest
import zope.component.hooks


def assert_fields_selected(browser, *fields):
    """Assert that some fields are selected in `event_additional_fields`."""
    assert (list(fields) ==
            browser.getControl(
                name='form.widgets.event_additional_fields.to').displayOptions)


def test_calendar__CalendarView__1(address_book, FieldFactory, browser):
    """It allows to select fields for display in the calendar."""
    field = FieldFactory(
        address_book, IEvent, u'Int', u'reservations').__name__
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    browser.getLink('Calendar view').click()
    assert browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL == browser.url
    browser.in_out_widget_select('form.widgets.event_additional_fields',
                                 [browser.getControl('persons'),
                                  browser.getControl('reservations')])
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL)
    assert_fields_selected(browser, 'reservations', 'persons')
    # It does not break on selected but deleted user defined field:
    with zope.component.hooks.site(address_book):
        event_entity = IEntity(IEvent)
        event_entity.removeField(event_entity.getRawField(field))
    browser.open(browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL)
    assert_fields_selected(browser, 'persons')


def test_calendar__CalendarView__2(address_book, browser):
    """It is not shown on calendar master data for a calendar visitor."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('Calendar view')


def test_calendar__CalendarView__3(address_book, browser):
    """It is not accessible for a calendar visitor."""
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.CALENDAR_MASTERDATA_EDIT_DISPLAY_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)
