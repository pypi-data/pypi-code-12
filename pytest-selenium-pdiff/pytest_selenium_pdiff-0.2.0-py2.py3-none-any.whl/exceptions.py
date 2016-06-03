class MissingScreenshot(Exception):
    def __init__(self, screenshot_name, screenshot_path, *args, **kwargs):
        message = 'Cannot find the screenshot named ' \
                  '"{}" at {}, screenshot capture is disabled.'

        message = message.format(screenshot_name,
                                 screenshot_path
                                 )

        super().__init__(message, *args, **kwargs)


class ScreenshotMismatch(Exception):
    def __init__(self, screenshot_name, screenshot_path, diff_path, pdiff_output, *args, **kwargs):
        message = 'Captured screenshot named "{}", does not match stored screenshot "{}".  ' \
                  'Diff is available at: "{}", perceptualdiff returned: {}.'

        message = message.format(
            screenshot_name,
            screenshot_path,
            diff_path,
            pdiff_output
        )

        super().__init__(message, *args, **kwargs)
