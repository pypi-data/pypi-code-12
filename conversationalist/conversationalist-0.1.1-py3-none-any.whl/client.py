import base64
import json
from os.path import expanduser
import re
import mandrill
import tweepy
import datetime
import pytz
from dateutil.parser import parse
from core import Timeline, TimelineEncoder, Conversation
from utils import write_tick_tock, upload_ticktock, ISO_WITH_OFFSET_DT_FORMAT
import settings


def set_pre_exchange_content(status):
    text = status['text']
    pre_content = ''
    # number check
    pattern1 = r'item\s*#?(\d+)'
    regex1 = re.compile(pattern1, re.I)
    match = regex1.search(text)
    if match:
        pre_content = int(match.group(1))
    # if not pre_content:
    #     # mention check
    #     term = 'item'
    #     pattern2 = r'\b%s\b' % term
    #     regex2 = re.compile(pattern2, re.I)
    #     match2 = regex2.search(text)
    #     if match2:
    #         pre_content = 'Item Mention'
    return pre_content


def ticktock1(api, name, hours):
    timeline = Timeline(api, name, hours)
    style_words = ['yeas', 'nays', 'abstentions', 'abstains', 'off the dais', 'off-the-dais']
    conversation = Conversation(timeline, timeline.start, timeline.cutoff,
                                style_words=style_words, pre_exchange=set_pre_exchange_content)
    file_path = '/Users/jga/dev/ticktock.html'
    write_tick_tock(file_path, conversation.data['title'],
                    conversation.data['hourlies'], conversation.participation.get_ranked_profiles(), conversation.nav)
    identifier = 'ticktock'
    upload_ticktock(file_path, identifier)




def pluck(api, name='@twitter'):
    batch = api.user_timeline(name)
    for tweet in batch:
        for k, v in tweet.__dict__.iteritems():
            print k, ': ', v
        break


def to_json(api, name, hours):
    timeline = Timeline(api, name, (hours * -1))
    with open('/Users/jga/dev/timeline.json', 'w') as outfile:
        json.dump(timeline, outfile, cls=TimelineEncoder, indent=2)


def get_json_file_path(path):
    timezone = pytz.timezone('America/Chicago')
    date_label = datetime.datetime.now(tz=timezone).strftime('%m%d%Y')
    return ''.join((path, 'conversationalist_data_', date_label,'.json'))


def get_output_file_path(path):
    timezone = pytz.timezone('America/Chicago')
    date_label = datetime.datetime.now(tz=timezone).strftime('%m%d%Y-%H%M')
    file_name = ''.join(('ticktock-', date_label,'.txt',))
    return ''.join((path, file_name)), file_name


def get_email_subject():
    timezone = pytz.timezone('America/Chicago')
    date_label = datetime.datetime.now(tz=timezone).strftime('%m-%d-%Y %H:%M')
    return ''.join(('Tick Tock File - ', date_label,))


def is_valid_payload(payload):
    keys = ['html', 'subject', 'text', 'to']
    for k in keys:
        if not k in payload:
            return False
    return True


def with_encoded(attachment_path, attachment_name):
    encoded_file = base64.b64encode(open(attachment_path, 'r').read())
    attachment = {
        'name': attachment_name,
        'content': encoded_file,
        'type': 'text/plain'
    }
    return attachment


def send_email(payload):
    if is_valid_payload(payload):
        subject = payload['subject']
        html_content = payload['html']
        text_content = payload['text']
        to_settings = payload['to']
        metadata = {'website': 'www.austinmonitor.com', 'process': 'ticktock'}
        tags = payload['tags'] if 'tags' in payload else []
        attachment = with_encoded(payload['attachment_path'], payload['attachment_name'])
        try:
            mandrill_client = mandrill.Mandrill(settings.mandrill_key)
            message = {
                'attachments': [attachment],
                'auto_html': True,
                'auto_text': True,
                #'bcc_address': 'message.bcc_address@example.com',
                'from_email': 'ticktock@austinmonitor.com',
                'from_name': 'Tick Tock App',
                #`'global_merge_vars': [{'content': 'merge1 content', 'name': 'merge1'}],
                #`'google_analytics_campaign': 'message.from_email@example.com',
                #'google_analytics_domains': ['example.com'],
                'headers': {'Reply-To': 'devjga@gmail.com'},
                'html': html_content,
                # 'images': [{'content': 'ZXhhbXBsZSBmaWxl',
                #              'name': 'IMAGECID',
                #              'type': 'image/png'}],
                'important': False,
                'inline_css': None,
                'merge': False,
                # 'merge_vars': [{'rcpt': 'recipient.email@example.com',
                #                  'vars': [{'content': 'merge2 content', 'name': 'merge2'}]}],
                'metadata': metadata,
                'preserve_recipients': False,
                #'recipient_metadata': [{'rcpt': 'recipient.email@example.com',
                #                         'values': {'user_id': 123456}}],
                #'return_path_domain': None,
                #'signing_domain': None,
                #'subaccount': 'customer-123',
                'subject': subject,
                'tags': tags,
                'text': text_content,
                'to': to_settings,
                'track_clicks': False,
                'track_opens': False,
                'tracking_domain': None,
                'url_strip_qs': True,
                'view_content_link': False}
            result = mandrill_client.messages.send(message=message, async=False)

        except mandrill.Error, e:
            # Mandrill errors are thrown as exceptions
            print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
            # A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'
            raise

            # url = 'https://mandrillapp.com/api/1.0/'
            # data = json.dumps(payload)
            # r = requests.post(url, data=data)
            # if r.status_code != 200:
            #     handle_email_error(r.text)


def ticktock2(name='@mkanin', hours=18):
    print 'Starting ticktock2...'
    auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
    auth.set_access_token(settings.access_token, settings.access_token_secret)
    api = tweepy.API(auth)
    style_words = ['yeas', 'nays', 'abstentions', 'abstains', 'off the dais', 'off-the-dais']
    t = Timeline(api, name, (hours * -1))
    filename = get_json_file_path('/Users/jga/conversationalist/json/')
    with open(filename, 'w') as outfile:
        json.dump(t, outfile, cls=TimelineEncoder, indent=1)
    print '...writing json...'
    with open(filename) as infile:
        timeline = json.load(infile)
    start = parse(timeline['start'])
    cutoff = parse(timeline['cutoff'])
    conversation = Conversation(timeline, start, cutoff, style_words=style_words,
                                pre_exchange=set_pre_exchange_content)
    output_file_path, output_file_name = get_output_file_path('/Users/jga/conversationalist/content/')
    print '...writing text file...'
    write_tick_tock(output_file_path, conversation.data['title'],
                    conversation.data['hourlies'], conversation.participation.get_ranked_profiles(), conversation.nav)
    #identifier = 'ticktock'
    #upload_ticktock(file_path, identifier)
    print '...ticktock2 done.'


def ticktock(twitter_username, hours, data_path=settings.data_path,
             output_path=settings.content_path, email=None, name=None):
    print 'Starting ticktock. Getting tweets...'
    auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
    auth.set_access_token(settings.access_token, settings.access_token_secret)
    api = tweepy.API(auth)
    style_words = ['yeas', 'nays', 'abstentions', 'abstains', 'off the dais', 'off-the-dais']
    t = Timeline(api, twitter_username, (hours * -1))
    json_file = get_json_file_path(data_path)
    print '...writing json...'
    with open(json_file, 'w') as outfile:
        json.dump(t, outfile, cls=TimelineEncoder, indent=1)
    with open(json_file) as infile:
        timeline = json.load(infile)
    start = parse(timeline['start'])
    cutoff = parse(timeline['cutoff'])
    conversation = Conversation(timeline, start, cutoff, style_words=style_words,
                                pre_exchange=set_pre_exchange_content)
    output_file_path, output_file_name = get_output_file_path(output_path)
    print '...writing content...'
    write_tick_tock(output_file_path, conversation.data['title'], conversation.data['hourlies'],
                    conversation.participation.get_ranked_profiles(), conversation.nav)
    if email:
        if not name:
            name = email
        subject = get_email_subject()
        payload = {
            'subject': subject,
            'html': '<p>Tick Tock file attached.</p>',
            'text': 'Tick Tock file attached.',
            'to': [{'email': email, 'name': name, 'type': 'to'}],
            'attachment_path': output_file_path,
            'attachment_name': output_file_name
        }
        print '...sending email to: ', email
        send_email(payload)
    print '...ticktock done.'


def print_rate_limit_info():
    auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
    auth.set_access_token(settings.access_token, settings.access_token_secret)
    api = tweepy.API(auth)
    status = api.rate_limit_status()
    for (k, v) in status['resources'].items():
        if k == 'statuses':
            for (k2, v2) in v.items():
                print ('KEY: ', k2, ' VALUE: ', v2)

#print_rate_limit_info()