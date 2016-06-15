import os
import shutil

from sh import perceptualdiff

from .exceptions import MissingScreenshot, ScreenshotMismatch
from .pytest_selenium_pdiff import settings
from .utils import ensure_path_exists


def screenshot_matches(driver, screenshot_name):
    storage_path = settings['SCREENSHOTS_PATH']
    artifacts_path = settings['PDIFF_PATH']

    stored_screenshot = os.path.join(storage_path, screenshot_name + '.png')
    diff_output_path = os.path.join(artifacts_path, screenshot_name + '.diff.png')
    captured_screenshot = os.path.join(artifacts_path, screenshot_name + '.captured.png')

    ensure_path_exists(os.path.dirname(stored_screenshot))
    ensure_path_exists(os.path.dirname(diff_output_path))

    have_stored_screenshot = os.path.exists(stored_screenshot)

    if not have_stored_screenshot and not settings['ALLOW_SCREENSHOT_CAPTURE']:
        raise MissingScreenshot(screenshot_name, stored_screenshot)

    driver.get_screenshot_as_file(captured_screenshot)

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

    return True
