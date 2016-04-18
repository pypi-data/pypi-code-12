from __future__ import unicode_literals
from hashlib import sha1
from drae import drae
from bender import Bot
from bender import final_step
from bender import next_step


class Def(Bot):
    commands = {'/def': 'search_word'}

    def __init__(self, dunno_sticker, go_away_sticker, *args, **kwargs):
        self.dunno_sticker = dunno_sticker
        self.go_away_sticker = go_away_sticker
        super(Def, self).__init__(*args, **kwargs)

    def handle_update(self, update):
        inline_query = update.get('inline_query', None)
        
        if inline_query:
            iq_id = inline_query['id']
            query = inline_query['query']

            if query != '':
                wx = drae.search(query)
            else:
                wx = []

            results = []

            if wx:
                if isinstance(wx, list):
                    for w in wx:
                        results.append({'type': 'article',
                                'id': sha1(w.word.encode('utf-8')).hexdigest(),
                                'title': w.word,
                                'description': 'define',
                                'input_message_content': {'message_text': w.text,
                                                          'disable_web_page_preview': True}})

                else:
                    results.append({'type': 'article',
                                    'id': sha1(wx.word.encode('utf-8')).hexdigest(),
                                    'title': wx.word,
                                    'description': 'define',
                                    'input_message_content': {'message_text': wx.text,
                                                              'disable_web_page_preview': True}})

            if results:
                import json
                import requests
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                method = 'answerInlineQuery'
                url = "https://api.telegram.org/bot%s/%s" % (self.token, method)
                data = {'inline_query_id': iq_id,
                        'results': results,
                        'cache_time': 300}
                requests.post(url, data=json.dumps(data), headers=headers)
            return True

        else:
            super(Def, self).handle_update(update)

    @next_step('define_word')
    def search_word(self, *args, **kwargs):
        word = kwargs.get('rest')
        wx = drae.search(word)

        if wx:
            if isinstance(wx, list):
                # this is ugly
                user_words_key = self.redis_prefix + str(self._message['chat']['id'])
                for w in wx:
                    # save this chat's word choice list
                    self.redis.sadd(user_words_key, w)

                    # save word info (global)
                    self.redis.sadd(self.redis_prefix + 'words', w.word)
                    word_key = self.redis_prefix + 'words:' + w.word
                    self.redis.hset(word_key, 'id', w.id)

                # return True => next step
                return self.reply({'text': 'Which one?',
                                   'reply_markup': {'keyboard': [[w.word for w in wx]],
                                                    'one_time_keyboard': True,
                                                    'selective': True}})
            else:
                word_key = self.redis_prefix + 'words:' + wx.word
                # see if it's cached
                cached_meaning = self.redis.hget(word_key, 'text')

                if cached_meaning:
                    self.reply({'text': cached_meaning})
                else:
                    # save word info (global)
                    self.redis.sadd(self.redis_prefix + 'words', wx.word)
                    self.redis.hset(word_key, 'id', wx.id)
                    self.redis.hset(word_key, 'text', wx.text)
                    self.reply({'text': wx.text})

                self.redis.hincrby(word_key, 'hits', 1)
        else:
            return self.reply({'sticker': self.dunno_sticker})

    @final_step
    def define_word(self, *args, **kwargs):
        word = self._message.get('text', '')
        user_words_key = self.redis_prefix + str(self._message['chat']['id'])
        if self.redis.sismember(user_words_key, word):
            word_key = self.redis_prefix + 'words:' + word
            word_id = self.redis.hget(word_key, 'id')
            cached_meaning = self.redis.hget(word_key, 'text')
            if cached_meaning:
                meaning = cached_meaning
            else:
                w = drae.Word(word, word_id)
                meaning = w.text
            self.reply({'text': meaning,
                        'reply_markup': {'hide_keyboard': True}})

            self.redis.delete(user_words_key)
            self.redis.hincrby(word_key, 'hits', 1)
            return True
        else:
            return self.reply({'sticker': self.go_away_sticker,
                               'reply_markup': {'hide_keyboard': True}})
