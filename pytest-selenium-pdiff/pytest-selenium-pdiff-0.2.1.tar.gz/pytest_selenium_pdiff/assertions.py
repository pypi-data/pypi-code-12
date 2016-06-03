import os
import shutil

from sh import perceptualdiff

from .exceptions import MissingScreenshot, ScreenshotMismatch
from .pytest_selenium_pdiff import settings
from .utils import ensure_path_exists, capture_screenshot


def assert_screenshot_matches(driver, screenshot_name):
    storage_path = settings['SCREENSHOTS_PATH']
    artifacts_path = settings['PDIFF_PATH']

    ensure_path_exists(storage_path)
    ensure_path_exists(artifacts_path)

    stored_screenshot = os.path.join(storage_path, screenshot_name + '.png')
    diff_output_path = os.path.join(artifacts_path, screenshot_name + '.diff.png')

    have_stored_screenshot = os.path.exists(stored_screenshot)

    if not have_stored_screenshot and not settings['ALLOW_SCREENSHOT_CAPTURE']:
        raise MissingScreenshot(screenshot_name, stored_screenshot)

    captured_screenshot = capture_screenshot(driver, screenshot_name)

    try:
        if have_stored_screenshot:
            result = perceptualdiff(
                '-output', diff_output_path,
                stored_screenshot,
                captured_screenshot,
                _ok_code=[0, 1]
            )

            if result.exit_code == 1:
                raise ScreenshotMismatch(screenshot_name, stored_screenshot, diff_output_path, str(result).strip())
        elif settings['ALLOW_SCREENSHOT_CAPTURE']:
            shutil.move(captured_screenshot, stored_screenshot)
    finally:
        if os.path.exists(captured_screenshot):
            os.unlink(captured_screenshot)
