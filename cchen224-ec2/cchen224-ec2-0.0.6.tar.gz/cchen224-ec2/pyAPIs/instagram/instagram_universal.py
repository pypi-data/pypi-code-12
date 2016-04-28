import sys
import time
import traceback

import httplib2
from instagram import InstagramAPIError
from instagram import InstagramClientError
from instagram.client import InstagramAPI
import datetime

from
from gmail_send import Gmail
from instagram_access_tokens import access_tokens
from progress_bar import ProgressBar


# pip install python-instagram
# pip install --upgrade google-api-python-client


class Instagram:

    def __init__(self, job):
        self._job = job
        self._account = 1
        self._extention = ''

        if 'follower' in job.lower():
            self._extention = '.followers'
        elif 'following' in job.lower() or 'friend' in job.lower():
            self._extention = '.following'

        self._gmail = Gmail().set_from_to()

    def set_access_token(self, i):
        self._account = i
        self._api = InstagramAPI(access_token=access_tokens[self._account])
        self._gmail = self._gmail.set_subject('AWS Instagram' + self._extention + '_' + str(i))
        return self

    def request(self, user_id, generator):
        c = 0
        nRetry = 0

        while True:
            if nRetry >= 10:
                break
            try:
                items, _next = generator.next()
                o = open(user_id + self._extention, 'a')
                c += 1
                for item in items:
                    o.write(item.id + '\n')
                sys.stdout.write(' User' + user_id + ': ' + str(c) + '\r')
                sys.stdout.flush()
                o.close()
                if _next:
                    time.sleep(0.72)
                else:
                    break
            except InstagramAPIError, e:
                if str(e.status_code) == '429':
                    time.sleep(60)
                    self._gmail = self._gmail.send_message('429ExceedsLimit.\n')
                    self._gmail = self._gmail.send_message(datetime.datetime.now().__str__() + '\n')
                    continue
                elif str(e.status_code) == '400':
                    self._gmail = self._gmail.send_message('400NotFound.\n')
                    break
            except httplib2.ServerNotFoundError:
                self._gmail = self._gmail.send_message('ServerNotFoundError\n')
                time.sleep(10)
                continue
            except InstagramClientError, e:
                nRetry += 1
                if str(e.error_message) == '402':
                    try:
                        self._gmail = self._gmail.send_message(user_id + ' ' + str(c) + '\n\n' + traceback.format_exc() + '\n\n')
                        self._gmail = self._gmail.close()
                    except:
                        pass
                time.sleep(5)
                continue
            except StopIteration:
                break
            except Exception:
                self._gmail = self._gmail.send_message('RequestError on page' + str(c) + '\n\n' + traceback.format_exc() + '\n\n')
                self._gmail = self._gmail.close()
                continue

    def loop(self, fp):
        i = open(fp, 'r')
        n = 0
        for _ in i:
            n += 1
        i.close()
        bar = ProgressBar(total=n)

        print 'Starting', '...'
        i = open(fp, 'r')
        for line in i:
            try:
                bar = bar.move().log()
                user_id = line.strip()
                self._gmail = self._gmail.send_message('User' + user_id)
                self.request(user_id,
                             {'.followers': self._api.user_followed_by(user_id=user_id, as_generator=True, max_pages=999999),
                              '.following': self._api.user_follows(user_id=user_id, as_generator=True, max_pages=999999)
                              }.get(self._extention))
                self._gmail = self._gmail.send_message('Done!\n')
            except KeyboardInterrupt:
                self._gmail = self._gmail.close()
                i.close()
                bar.close()
                return False
        self._gmail = self._gmail.send_message('\n' + fp + ' Done.\n')
        self._gmail = self._gmail.close()
        i.close()
        bar.close()
        return True

    def test(self, user_id):
        self.request(user_id,
                     {'.followers': self._api.user_followed_by(user_id=user_id, as_generator=True, max_pages=999999),
                      '.following': self._api.user_follows(user_id=user_id, as_generator=True, max_pages=999999)
                      }.get(self._extention))


if __name__ == '__main__':
    argvs = sys.argv[1:]
    job_name = argvs[0]
    filepath = argvs[1]
    server = int(argvs[2])
    ins = Instagram(job_name).set_access_token(server).loop(filepath)


Instagram('followers').set_access_token(19).test('294211877')