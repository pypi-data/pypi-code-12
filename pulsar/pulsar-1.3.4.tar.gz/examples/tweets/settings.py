from config import *    # noqa

twitter_api_key = 's8KXEZziHgqxTQy962p4Q'
twitter_api_secret = 'FL2A3pzdKLfznC7o3HAYaKqHMdpuGmUGlJYnVTwpsA'
twitter_access_token = '19934307-zaUhqhvq79PjL62eTsOSQeTXAn9Omv2Tg6AxxHBCI'
twitter_access_secret = 'bR4hzVCyfmmuH6wAibCadJ7sedNQUuxkliwSFxCLd4'

twitter_stream_filter = {'track': 'python'}


def test_twitter():
    from pulsar.apps.http import HttpClient, OAuth1
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'

    def new_data(response, data=None):
        body = response.recv_body()
        print(body)

    http = HttpClient(encode_multipart=False)
    oauth1 = OAuth1(twitter_api_key,
                    client_secret=twitter_api_secret,
                    resource_owner_key=twitter_access_token,
                    resource_owner_secret=twitter_access_secret)
    http.bind_event('pre_request', oauth1)
    response = http.post(url, data={'track': 'twitter'},
                         data_processed=new_data)
    print(response.status_code)


if __name__ == '__main__':
    test_twitter()
