
import click
from mh_cli import cli
from time import sleep

from selenium.common.exceptions import TimeoutException
from common import pass_state, init_browser, selenium_options
from mh_pages.pages import RecordingsPage, \
    AdminPage, \
    TrimPage, \
    UploadPage


@cli.group()
def rec():
    """Do stuff with Matterhorn recordings"""


@rec.command()
@click.option('--presenter',
              help="Presenter video")
@click.option('--presentation',
              help="Presentation video")
@click.option('--combined',
              help="Combined presenter/presentation video")
@click.option('--series',
              help="Series title. Should match an existing series.")
@click.option('--title', default='mh-ui-testing upload',
              help="Recording title")
@click.option('--type', default='L01',
              help="Recording type")
@click.option('-i', '--inbox', is_flag=True,
              help="Use a MH inbox media file")
@click.option('--live_stream', is_flag=True,
              help="Flag to indicate a live stream recording")
@selenium_options
@pass_state
@init_browser('/admin')
def upload(state, presenter, presentation, combined,
           series, title, type, inbox, live_stream):
    """Upload a recording from a local path or the inbox"""

    page = RecordingsPage(state.browser)
    sleep(2)

    with page.wait_for_page_change():
        page.upload_recording_button.click()

    page = UploadPage(state.browser)
    page.title_input.type(title)
    page.type_input.type(type)

    if series is not None:
        page.set_series(series)

    page.set_upload_files(presenter=presenter,
                          presentation=presentation,
                          combined=combined,
                          is_inbox=inbox)

    if live_stream:
        page.live_stream_checkbox.check()
    else:
        page.live_stream_checkbox.uncheck()

    if combined is not None:
        page.multitrack_checkbox.check()
    else:
        page.multitrack_checkbox.uncheck()

    page.upload_button.click()
    page.wait_for_upload_finish()


@rec.command()
@click.option('-f', '--filter')
@click.option('-c', '--count', type=int, default=None)
@selenium_options
@pass_state
@init_browser('/admin')
def trim(state, filter=None, count=None):
    """Execute trims on existing recording(s)"""

    page = AdminPage(state.browser)
    page.recordings_tab.click()
    page = RecordingsPage(state.browser)
    page.max_per_page()
    page.on_hold_tab.click()

    if filter is not None:
        field, value = filter.split(':', 1)
        page.filter_recordings(field, value)

    link_idx = 0
    while True:

        # kinda annoying that we have to do this each time
        page.refresh_off()
        sleep(1)

        try:
            # re-resolve the trim link elements each time because the refs go
            # stale when the page reloads
            # also, iterate via incrementing idx so that we don't somehow trim
            # the same thing > once (e.g. the entry doesn't get removed from
            # the table because the workflow hasn't actually resumed)
            link = page.trim_links[link_idx]
        except (TimeoutException, IndexError):
            break

        href = link['href']
        scheme, js = href.split(':', 1)
        page.js(js)
        page = TrimPage(state.browser)
        with page.switch_frame(page.trim_iframe):
            page.trim()

        with page.wait_for_page_change():
            page.reload()

        page = RecordingsPage(state.browser)

        if count is not None:
            count -= 1
            if count == 0:
                break
