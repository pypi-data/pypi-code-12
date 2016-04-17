# coding=utf-8

from __future__ import print_function, unicode_literals

import base64
import getpass
import os

import requests

from .oauth.before_login_auth import BeforeLoginAuth
from .oauth.zhihu_oauth import ZhihuOAuth
from .oauth.token import ZhihuToken
from .oauth.setting import (
    CAPTCHA_URL, LOGIN_URL, LOGIN_DATA, CLIENT_ID, APP_SECRET
)
from .oauth.utils import login_signature
from .setting import CAPTCHA_FILE, RE_FUNC_MAP
from .utils import need_login, int_id
from .exception import (
    UnexpectedResponseException, NeedCaptchaException, MyJSONDecodeError
)

__all__ = ['ZhihuClient']

try:
    # noinspection PyShadowingBuiltins,PyUnresolvedReferences
    input = raw_input
except NameError:
    pass

try:
    bs64decode = base64.decodebytes
except AttributeError:
    # for python 2
    # noinspection PyDeprecation
    bs64decode = base64.decodestring


class ZhihuClient:
    def __init__(self, client_id=None, secret=None):
        """
        知乎客户端，这是获取所有类的入口。

        :param str|unicode client_id: 客户端 ID。
        :param str|unicode secret: 客户端 ID 对应的 SECRET KEY。
        :rtype: :class:`.ZhihuClient`
        """
        self._session = requests.session()
        # client_id and secret shouldn't have default value
        # after zhihu open api
        self._client_id = client_id or CLIENT_ID
        self._secret = secret or APP_SECRET
        self._login_auth = BeforeLoginAuth(self._client_id)
        self._token = None

    def need_captcha(self):
        """
        ..  note::

            一般来说此方法不需要手动调用。

            在调用 :meth:`.login` 时捕获 :class:`.NeedCaptchaException` 即可。

            而 :meth:`.login_in_terminal` 会自动处理需要验证码的情况。

        :return: 下次登录是否需要验证码。
        :rtype: bool
        :raise: :class:`.UnexpectedResponseException` 知乎返回的数据和预期格式不符。
        """
        res = self._session.get(CAPTCHA_URL, auth=self._login_auth)
        try:
            j = res.json()
            return j['show_captcha']
        except (MyJSONDecodeError, KeyError):
            # noinspection PyTypeChecker
            raise UnexpectedResponseException(
                CAPTCHA_URL, res,
                'a json data with show_captcha item'
            )

    def get_captcha(self):
        """
        :return: 如果需要验证码，则返回 bytes 型验证码，不需要则返回 None。
        :rtype: None | bytes
        :raise: :class:`.UnexpectedResponseException` 知乎返回的数据和预期格式不符
        """
        if self.need_captcha():
            res = self._session.put(CAPTCHA_URL, auth=self._login_auth)
            try:
                j = res.json()
                return bs64decode(j['img_base64'].encode('utf-8'))
            except (MyJSONDecodeError, ValueError, KeyError):
                raise UnexpectedResponseException(
                    CAPTCHA_URL,
                    res,
                    'a json string contain a img_base64 item.'
                )
        return None

    def login(self, email, password, captcha=None):
        """
        登录知乎的主要方法。

        :param str|unicode email: 邮箱。
        :param str|unicode password: 密码。
        :param str|unicode captcha: 验证码，可以为空。

        :return: 二元元组，第一个元素表示是否成功，第二个元素表示失败原因。
        :rtype: tuple(bool, str)
        :raise: :class:`.NeedCaptchaException` 此次登录需要验证码
        """

        if captcha is None:
            try:
                if self.need_captcha():
                    raise NeedCaptchaException
            except UnexpectedResponseException:
                return False, 'UnexpectedResponse'
        else:
            res = self._session.post(
                CAPTCHA_URL,
                auth=self._login_auth,
                data={'input_text': captcha}
            )
            try:
                json_dict = res.json()
                if 'error' in json_dict:
                    return False, json_dict['error']['message']
            except (MyJSONDecodeError, ValueError, KeyError):
                return False, 'UnexpectedResponse'

        data = dict(LOGIN_DATA)
        data['username'] = email
        data['password'] = password
        data['client_id'] = self._client_id

        login_signature(data, self._secret)
        res = self._session.post(LOGIN_URL, auth=self._login_auth, data=data)
        try:
            json_dict = res.json()
            if 'error' in json_dict:
                return False, json_dict['error']['message']
            else:
                self._token = ZhihuToken.from_dict(json_dict)
                self._session.auth = ZhihuOAuth(self._token)
                return True, ''
        except (MyJSONDecodeError, ValueError, KeyError):
            return False, 'UnexpectedResponse'

    def login_in_terminal(self, email=None, password=None):
        """
        为在命令行模式下使用本库的用户提供的快捷登录方法。

        在未提供 email 或 password 参数时会在终端中请求输入。

        ..  note:: 此方法会自动处理验证码需要验证码情况。

        :param str|unicode email: 邮箱，可能手机号也可以吧，我没测试。
        :param str|unicode password: 密码咯。
        :return: .. seealso:: :meth:`.login`
        """
        print('----- Zhihu OAuth Login -----')
        email = email or input('email: ')
        password = password or getpass.getpass('password: ')

        try:
            success, reason = self.login(email, password)
        except NeedCaptchaException:
            print('Need for a captcha, getting it......')
            captcha_image = self.get_captcha()
            with open('captcha.gif', 'wb') as f:
                f.write(captcha_image)
            print('Please open {0} for captcha'.format(
                os.path.abspath(CAPTCHA_FILE)))
            captcha = input('captcha: ')
            os.remove(os.path.abspath(CAPTCHA_FILE))
            success, reason = self.login(email, password, captcha)
        if success:
            print('Login success.')
        else:
            print('Login failed, reason: ', reason)

        return success, reason

    def create_token(self, filename, email=None, password=None):
        """
        另一个快捷方法，作用为调用 :meth:`.login_in_terminal`

        如果成功则将 token 储存文件中。

        :param str|unicode filename: token 保存的文件名
        :param str|unicode email: 邮箱，手机不知道可不可以
        :param str|unicode password: 密码
        :return: .. seealso:: :meth:`.login`
        """
        success, reason = self.login_in_terminal(email, password)
        if success:
            self.save_token(filename)
            print('Token file created success.')
        else:
            print('Token file created failed.')
        return success, reason

    def load_token(self, filename):
        """
        通过载入 token 文件来达到登录状态。

        ..  seealso:: :meth:`.save_token`

        :param str|unicode filename: token 文件名。
        :return: 无返回值，也就是说其实不知道是否登录成功。
        """
        self._token = ZhihuToken.from_file(filename)
        self._session.auth = ZhihuOAuth(self._token)

    @need_login
    def save_token(self, filename):
        """
        将通过登录获取到的 token 保存为文件，必须是已登录状态才能调用。

        ..  seealso:: :meth:`.load_token`

        :param str|unicode filename: 将 token 储存为文件。
        :return: 无返回值。
        """
        self._token.save(filename)

    def is_login(self):
        """
        :return: 是否已登录。但其实只是检查内部的 token 是否是 None。
        :rtype: bool
        """
        return self._token is not None

    @need_login
    def test_api(self, method, url, params=None, data=None):
        """
        开发时用的测试某个 API 返回的 JSON 用的便捷接口。

        :param str|unicode method: HTTP 方式， GET or POST or OPTION, etc。
        :param str|unicode url: API 地址。
        :param dict params: GET 参数。
        :param dict data: POST 参数。
        :return: 访问结果。
        :rtype: request.Response
        """
        return self._session.request(method, url, params, data)

    def set_proxy(self, proxy):
        """ 设置 http 和 https 代理（不支持 socks 代理）

        因为由 :any:`ZhihuClient` 生成的知乎类对象和本对象使用同一
        session，所以设置代理后，对所有由当前对象生成的知乎对象均会
        使用设置的代理。

        :param str|unicode proxy: 形如 '10.10.1.10:3128'，传入 None
          表示清除代理设置。
        :return: None
        """
        if proxy is None:
            self._session.proxies.clear()
            self._session.verify = True
        else:
            self._session.proxies.update({'http': proxy, 'https': proxy})
            self._session.verify = False

    # ----- get zhihu classes from ids -----

    @int_id
    @need_login
    def answer(self, aid):
        """
        获取答案对象，需要 Client 是登录状态。

        :param int aid: 答案 ID。
        :举例:
            https://www.zhihu.com/question/xxxxxx/answer/1234567
            的答案 ID 是 1234567。
        :rtype: Answer
        """
        from .zhcls.answer import Answer
        return Answer(aid, None, self._session)

    @int_id
    @need_login
    def article(self, aid):
        """
        获取文章对象，需要 Client 是登录状态。

        :param int aid: 文章 ID。
        :举例: https://zhuanlan.zhihu.com/p/1234567 的文章 ID 是 1234567。
        :rtype: :class:`Article`
        """
        from .zhcls.article import Article
        return Article(aid, None, self._session)

    @int_id
    @need_login
    def collection(self, cid):
        """
        获取收藏夹对象，需要 Client 是登录状态。

        :param int cid: 收藏夹 ID
        :举例: https://www.zhihu.com/collection/1234567 的收藏夹 ID 是 1234567。
        :rtype: :class:`Collection`
        """
        from .zhcls.collection import Collection
        return Collection(cid, None, self._session)

    @need_login
    def column(self, cid):
        """
        获取专栏对象，需要 Client 是登录状态。

        :param str|unicode cid: 专栏 ID，注意，类型是字符串。
        :举例: https://zhuanlan.zhihu.com/abcdefg 的专栏 ID 是 abcdefg。
        :rtype: :class:`Column`
        """
        from .zhcls.column import Column
        return Column(cid, None, self._session)

    @need_login
    def me(self):
        """
        获取当前登录的用户，需要 Client 是登录状态。

        ..  note::
            :class:`Me` 类继承于 :class:`People`，是一个不同于其他用户的类。
            这个类用于提供各种操作，比如点赞，评论，私信等。

        :rtype: :class:`Me`
        """

        from .zhcls import Me
        return Me(self._token.user_id, None, self._session)

    @need_login
    def people(self, pid):
        """
        获取用户对象，需要 Client 是登录状态。

        :param str|unicode pid: 用户 ID，注意，类型是字符串。
        :举例: https://www.zhihu.com/people/abcdefg 的用户 ID 是 abcdefg。
        :rtype: :class:`Column`
        """
        from .zhcls.people import People
        return People(pid, None, self._session)

    @int_id
    @need_login
    def question(self, qid):
        """
        获取问题对象，需要 Client 是登录状态。

        :param int qid: 问题 ID。
        :举例: https://www.zhihu.com/question/1234567 的问题 ID 是 1234567。
        :rtype: :class:`Question`
        """
        from .zhcls.question import Question
        return Question(qid, None, self._session)

    @int_id
    @need_login
    def topic(self, tid):
        """
        获取话题对象，需要 Client 是登录状态。

        :param int tid: 话题 ID。
        :举例: https://www.zhihu.com/tipoc/1234567 的话题 ID 是 1234567。
        :rtype: :class:`Topic`
        """
        from .zhcls.topic import Topic
        return Topic(tid, None, self._session)

    @need_login
    def from_url(self, url):
        """
        通过知乎的 URL 创建对象，需要 client 是登录状态。

        对象的 URL 请参见对应方法的描述。如 :any:`Answer` 类的 URL 的描述在
        :any:`ZhihuClient.answer` 方法的文档里，其余类似。

        ..  note:: 提示

            本方法也支持省略了开头的 ``https://``，或者结尾有多余的 ``/`` 的 URL。

        :param str|unicode url: 知乎对象的网址
        :return: 对应的知乎对象
        """
        for re, val in RE_FUNC_MAP.items():
            match = re.match(url)
            if match:
                zhihu_obj_id = match.group(1)
                func_name, need_int_id = val
                if need_int_id:
                    zhihu_obj_id = int(zhihu_obj_id)
                return getattr(self, func_name)(zhihu_obj_id)
        raise ValueError('Invalid zhihu object url!')
