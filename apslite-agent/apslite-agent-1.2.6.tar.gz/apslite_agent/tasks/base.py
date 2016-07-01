import timeit


class Task(object):
    name = ''

    class TaskError(Exception):
        pass

    def run(self):
        raise NotImplementedError()

    def __wrapper(self, result):
        return {
            'result': result,
        }

    def result(self, status, message='', data=None):
        if not data:
            data = {}

        result = {
            'type': 'task_result',
            'status': status,
            'message': message,
            'data': data,
        }

        return self.__wrapper(result)

    def __call__(self, data):
        timer = timeit.default_timer
        start = timer()
        self.data = data

        try:
            result = self.run()
        except Task.TaskError as e:
            result = self.__wrapper({
                'status': 'error',
                'message': str(e)
            })
        except Exception as e:
            result = self.__wrapper({
                'status': 'error',
                'message': str(e)
            })

        end = timer()

        result['elapsed'] = end - start

        return result
