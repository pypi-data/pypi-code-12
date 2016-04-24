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
        self.word_set_key = self.redis_prefix + 'words'

    def _get_word_key(self, query):
        return ':'.join([self.word_set_key, str(query)])

    def _get_user_words_key(self, chat_id):
        return self.redis_prefix + str(chat_id)

    def _add_word_choice(self, word, chat_id):
        self.redis.sadd(self._get_user_words_key(chat_id), word)

    def _word_in_choices(self, query, chat_id):
        return self.redis.sismember(self._get_user_words_key(chat_id), str(query))

    def _delete_choices(self, chat_id):
        self.redis.delete(self._get_user_words_key(chat_id))

    def _initialize_word(self, word):
        self.redis.sadd(self.word_set_key, word)
        self.redis.hset(self._get_word_key(word), 'id', word.id)

    def _cache_word_meaning(self, word):
        self._initialize_word(word)
        self.redis.hset(self._get_word_key(word), 'text', word.text)

    def _get_word_from_cache(self, query):
        cached_word = self.redis.hgetall(self._get_word_key(query))
        if cached_word:
            meaning = cached_word.get('text', None)
            return meaning, drae.Word(query, cached_word['id'], text=meaning)
        else:
            return [False, None]

    def _hit_word(self, word):
        self.redis.hincrby(self._get_word_key(word), 'hits', 1)

    def _inline_query_result_article(self, word):
        meaning, cached_word = self._get_word_from_cache(word.word)
        if meaning:
            word = cached_word
        else:
            self._cache_word_meaning(word)

        article = {'type': 'article',
                   'id': sha1(word.word.encode('utf-8')).hexdigest(),
                   'title': word.word,
                   'description': 'define',
                   'input_message_content': {'message_text': word.text,
                                             'disable_web_page_preview': True}}
        return article

    def handle_inline(self, query):
        wx = drae.search(query['query'])
        self.answer_inline_query(query['id'],
                                 [self._inline_query_result_article(w) for w in wx])

    @next_step('define_word')
    def search_word(self, *args, **kwargs):
        word = kwargs.get('rest')
        wx = drae.search(word)

        if wx:
            if len(wx) > 1:
                for w in wx:
                    # add words to the keyboard menu
                    self._add_word_choice(w, self._message['chat']['id'])
                    self._initialize_word(w)

                # return True => next step
                return self.reply({'text': 'Which one?',
                                   'reply_markup': {'keyboard': [[w.word for w in wx]],
                                                    'one_time_keyboard': True,
                                                    'selective': True}})
            else:
                meaning, cached_word = self._get_word_from_cache(wx[0].word)
                if meaning:
                    self.reply({'text': meaning})
                else:
                    self._cache_word_meaning(wx[0])
                    self.reply({'text': wx[0].text})
                self._hit_word(wx[0])
        else:
            self.reply({'sticker': self.dunno_sticker})

    @final_step
    def define_word(self, *args, **kwargs):
        word = self._message.get('text', '')

        if self._word_in_choices(word, self._message['chat']['id']):
            meaning, cached_word = self._get_word_from_cache(word)
            if not meaning:
                w = drae.Word(word, cached_word.id)
                meaning = w.text
                self._cache_word_meaning(w)

            self._delete_choices(self._message['chat']['id'])
            self._hit_word(word)
            return self.reply({'text': meaning,
                               'reply_markup': {'hide_keyboard': True}})
        else:
            return self.reply({'sticker': self.go_away_sticker,
                               'reply_markup': {'hide_keyboard': True}})
