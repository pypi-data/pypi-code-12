import os
import tempfile


def ensure_path_exists(path):
    path = str(path)

    if not os.path.exists(path):
        os.makedirs(path)


def capture_screenshot(driver, test_name, suffix='.png'):
    """
    Graciously borrowed from https://github.com/cobrateam/splinter/

    """
    test_name = test_name or ''

    (fd, filename) = tempfile.mkstemp(prefix=test_name, suffix=suffix)

    driver.get_screenshot_as_file(filename)

    return filename
