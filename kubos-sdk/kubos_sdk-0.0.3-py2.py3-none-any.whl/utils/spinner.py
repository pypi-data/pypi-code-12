#!/usb/bin/python


class StatusSpinner(threading._Timer):
    def run(self):
        spinner = self.get_spinner()
        while True:
            sys.stdout.write(spinner.next())
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')

    def get_spinner(self):
        while True:
            for symbol in '|/-\\':
                yield symbol


def start_spinner():
    spinner = StatusSpinner(0.1, None)
    spinner.daemon = True
    spinner.start()
    return spinner


def stop_spinner(spinner):
    spinner.cancel()

