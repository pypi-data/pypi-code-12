
from community_sift.communitysift import CommunitySift
import unittest

communitysift = CommunitySift()

input_data_chat_bad_words = {
    "room": "test_room",
    "language": "en",
    "text": "I want you to havesecswithme",
    "game name":"club penguin"
}

input_data_chat_good_words = {
    "room": "Lobby",
    "language": "en",
    "text": "hello, how are you",
    "rule": 1,
    "server": "Gamma",
    "player": 3455643,
    "player_display_name": "Stinky Feet"
}

input_data_username_bad = {
    "player_id": "12345",
    "username": "v@gina",
    "rule": "1",
    "language": "en"
}

input_data_username_good = {
    "player_id": "12345",
    "username": "john doe",
    "rule": "1",
    "language": "en"
}


class TestCS(unittest.TestCase):

    def test_chat_filter_bad_word(self):
        resp_bad = communitysift.execute('filterChats', input_data_chat_bad_words)
        assert resp_bad[0] == False

        resp_good = communitysift.execute('filterChats', input_data_chat_good_words)
        assert resp_good[0] == True


    def test_username_validator_bad_username(self):
        bad_username = communitysift.execute('userNameValidation', input_data_username_bad)
        assert bad_username[0] == False

        good_username = communitysift.execute('userNameValidation', input_data_username_good)
        assert good_username[0] == True

if __name__ == '__main__':
    unittest.main()
