import random

from komodo.core_modules.base import CheckBase


class RandomNumbers(CheckBase):
    def register_checks(self):
        yield "* * * * *", self.every_minute

    def every_minute(self, time):
        yield 'number', random.randint(1, 1000)
        yield 'number2', {
            'value': random.randint(1, 1000),
            'last': random.randint(1, 1000)
        }
        yield 'list', [random.randint(1, 1000) for _ in range(10)]
        yield 'float', round(random.random() * 1000, 2)
        yield 'graph', {
            'value': '30 ms',
            'labels': [i for i in range(10)],
            'series': [
                { 'name': 'one', 'data': [random.randint(1, 100) for _ in range(10)] },
                { 'name': 'two', 'data': [random.randint(1, 100) for _ in range(10)] }
            ],
        }

class RandomStatus(CheckBase):
    def register_checks(self):
        yield '* * * * *', self.make_status

    def make_status(self, time):
        yield 'status1', [
            {
                'title': 'Status {}'.format(i+1),
                'value': random.randint(0, 60),
                'status': random.choice([True, True, True, False])
            }
            for i in range(5)
        ]
        yield 'status2', [
            {
                'title': 'Status {}'.format(i+11),
                'value': random.randint(0, 60),
            }
            for i in range(8)
        ]
