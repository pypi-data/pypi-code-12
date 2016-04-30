import sys
import time
import traceback
import socket

import httplib2
from instagram import InstagramAPIError
from instagram import InstagramClientError
from instagram.client import InstagramAPI
import datetime

from cutils.gmail import Gmail
from cutils.progress_bar import ProgressBar
from pyAPIs.instagram.access_tokens import access_tokens


class Instagram:

    def __init__(self, job):
        self._job = job
        self._account = 1
        self._extention = ''
        self._output = ''

        if 'follower' in job.lower():
            self._extention = '.followers'
        elif 'following' in job.lower() or 'friend' in job.lower():
            self._extention = '.following'
        elif 'photo' in job.lower() or 'media' in job.lower():
            self._extention = '.media'

        self._gmail = Gmail().set_from_to()

    def set_access_token(self, i):
        self._account = i
        self._api = InstagramAPI(access_token=access_tokens[self._account])
        self._gmail = self._gmail.set_subject('AWS Instagram' + self._extention + '_' + str(i))
        return self

    def set_output(self, output):
        self._output = output
        return self

    def request(self, user_id, generator):
        c = 0
        n_retries_client = 0
        n_retries_socket = 0
        is_continue = True

        while True:
            if n_retries_client >= 10 or n_retries_socket >= 10:
                break
            try:
                items, _next = generator.next()

                if self._output == '':
                    o = open(user_id + self._extention, 'a')
                else:
                    o = open(self._output, 'a')

                c += 1
                for item in items:
                    if self._extention in ['.followers', '.following']:
                        o.write(user_id + '\t' + item.id + '\n')
                    elif self._extention == '.media':
                        from get_photo_per_user import get_photo_per_user
                        o.write(','.join(get_photo_per_user(item)) + '\n')
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
                    self._gmail = self._gmail.send_message('429ExceedsLimit...')
                    self._gmail = self._gmail.send_message(datetime.datetime.now().__str__() + '\n')
                    continue
                elif str(e.status_code) == '400':
                    self._gmail = self._gmail.send_message('400NotFound...')
                    break
            except httplib2.ServerNotFoundError:
                self._gmail = self._gmail.send_message('ServerNotFoundError...')
                time.sleep(10)
                continue
            except InstagramClientError, e:
                n_retries_client += 1
                if str(e.error_message) == '402':
                    try:
                        Gmail(0).set_from_to().set_subject('AWS Instagram' + self._extention + ' Client402Error!')\
                            .send_message(user_id + '@token' + str(self._account) + ' ' + str(c) +
                                          '\n\n' + traceback.format_exc() + '\n\n')
                    except:
                        pass
                time.sleep(5)
                continue
            except socket.error:
                n_retries_socket += 1
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                is_continue = False
                Gmail().set_from_to().set_subject('AWS Instagram' + self._extention + ' Stopped!')\
                    .send_message(user_id + '@access_token ' + str(self._account)).close()
                continue
            except StopIteration:
                return is_continue
            except Exception:
                Gmail().set_from_to().set_subject('AWS Instagram' + self._extention + ' Error!')\
                    .send_message(user_id + '\nRequestError on page' + str(c) +
                                  '\n\n' + traceback.format_exc() + '\n\n').close()
                continue
        return is_continue

    def loop(self, fp):
        i = open(fp, 'r')
        n = 0
        for _ in i:
            n += 1
        i.close()
        bar = ProgressBar(total=n)

        print 'Starting', '...'
        i = open(fp, 'r')
        is_continue = True
        for line in i:
            if is_continue:
                bar = bar.move().log()
                user_id = line.strip()
                self._gmail = self._gmail.send_message('User' + user_id)
                is_continue = self.request(user_id,
                                           {'.followers': self._api.user_followed_by(user_id=user_id, as_generator=True, max_pages=999999),
                                            '.following': self._api.user_follows(user_id=user_id, as_generator=True, max_pages=999999),
                                            '.media': self._api.user_recent_media(user_id=user_id, as_generator=True, max_pages=60)
                                            }.get(self._extention))
                self._gmail = self._gmail.send_message('Done!\n')
        self._gmail = self._gmail.send_message('\n' + fp + ' Done.\n')
        self._gmail = self._gmail.close()
        i.close()
        bar.close()
        return True

    def test(self, user_id):
        self.request(user_id,
                     {'.followers': self._api.user_followed_by(user_id=user_id, as_generator=True, max_pages=999999),
                      '.following': self._api.user_follows(user_id=user_id, as_generator=True, max_pages=999999),
                      '.media': self._api.user_recent_media(user_id=user_id, as_generator=True, max_pages=60)
                      }.get(self._extention))


# if __name__ == '__main__':
#     argvs = sys.argv[1:]
#     job_name = argvs[0]
#     filepath = argvs[1]
#     server = int(argvs[2])
#     ins = Instagram(job_name).set_access_token(server).loop(filepath)


# Instagram('followers').set_access_token(19).test('294211877')