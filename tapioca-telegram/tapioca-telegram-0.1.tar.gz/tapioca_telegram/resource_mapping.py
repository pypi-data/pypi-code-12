# coding: utf-8

RESOURCE_MAPPING = {
    # Available Methods
    # https://core.telegram.org/bots/api#available-methods
    'get_me': {
        'resource': 'getMe',
        'docs': 'https://core.telegram.org/bots/api#getme',
    },
    'send_message': {
        'resource': 'sendMessage',
        'docs': 'https://core.telegram.org/bots/api#sendmessage',
    },
    'forward_message': {
        'resource': 'forwardMessage',
        'docs': 'https://core.telegram.org/bots/api#forwardmessage',
    },
    'send_photo': {
        'resource': 'sendPhoto',
        'docs': 'https://core.telegram.org/bots/api#sendphoto',
    },
    'send_audio': {
        'resource': 'sendAudio',
        'docs': 'https://core.telegram.org/bots/api#sendaudio',
    },
    'send_document': {
        'resource': 'sendDocument',
        'docs': 'https://core.telegram.org/bots/api#senddocument',
    },
    'send_sticker': {
        'resource': 'sendSticker',
        'docs': 'https://core.telegram.org/bots/api#sendsticker',
    },
    'send_video': {
        'resource': 'sendVideo',
        'docs': 'https://core.telegram.org/bots/api#sendvideo',
    },
    'send_voice': {
        'resource': 'sendVoice',
        'docs': 'https://core.telegram.org/bots/api#sendvoice',
    },
    'send_location': {
        'resource': 'sendLocation',
        'docs': 'https://core.telegram.org/bots/api#sendlocation',
    },
    'send_venue': {
        'resource': 'sendVenue',
        'docs': 'https://core.telegram.org/bots/api#sendvenue',
    },
    'send_contact': {
        'resource': 'sendContact',
        'docs': 'https://core.telegram.org/bots/api#sendcontact',
    },
    'send_chat_action': {
        'resource': 'sendChatAction',
        'docs': 'https://core.telegram.org/bots/api#sendchataction',
    },
    'get_user_profile_photos': {
        'resource': 'getUserProfilePhotos',
        'docs': 'https://core.telegram.org/bots/api#getuserprofilephotos',
    },
    'get_file': {
        'resource': 'getFile',
        'docs': 'https://core.telegram.org/bots/api#getfile',
    },
    'kick_chat_member': {
        'resource': 'kickChatMember',
        'docs': 'https://core.telegram.org/bots/api#kickchatmember',
    },
    'leave_chat': {
        'resource': 'leaveChat',
        'docs': 'https://core.telegram.org/bots/api#leavechat',
    },
    'unban_chat_member': {
        'resource': 'unbanChatMember',
        'docs': 'https://core.telegram.org/bots/api#unban_chat_member',
    },
    'get_chat': {
        'resource': 'getChat',
        'docs': 'https://core.telegram.org/bots/api#getchat',
    },
    'get_chat_administrators': {
        'resource': 'getChatAdministrators',
        'docs': 'https://core.telegram.org/bots/api#getchatadministrators',
    },
    'get_chat_members_count': {
        'resource': 'getChatMembersCount',
        'docs': 'https://core.telegram.org/bots/api#getchatmemberscount',
    },
    'get_chat_member': {
        'resource': 'getChatMember',
        'docs': 'https://core.telegram.org/bots/api#getchatmember',
    },
    'answer_callback_query': {
        'resource': 'answerCallbackQuery',
        'docs': 'https://core.telegram.org/bots/api#answercallbackquery',
    },

    # Updating messages
    # https://core.telegram.org/bots/api#updating-messages
    'edit_message_text': {
        'resource': 'editMessageText',
        'docs': 'https://core.telegram.org/bots/api#editMessageText',
    },
    'edit_message_caption': {
        'resource': 'editMessageCaption',
        'docs': 'https://core.telegram.org/bots/api#editmessagecaption',
    },
    'edit_message_reply_markup': {
        'resource': 'editMessageReplyMarkup',
        'docs': 'https://core.telegram.org/bots/api#editmessagereplymarkup',
    },

    # Inline mode
    # https://core.telegram.org/bots/api#inline-mode
    'answer_inline_query': {
        'resource': 'answerInlineQuery',
        'docs': 'https://core.telegram.org/bots/api#answerinlinequery',
    },
}
