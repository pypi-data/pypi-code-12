import requests


class FirebaseClient:
    _http_google_message_api = 'https://fcm.googleapis.com/fcm/send'
    _http_google_notification_api = \
        'https://android.googleapis.com/gcm/notification'

    _notification_required_fields = ('body', 'title',)
    _notification_allowed_fields = ['icon'].append(
        _notification_required_fields)

    ALLOWED_PROTOCOLS = ('http',)  # later we will support xmpp

    def __init__(self, auth_key, protocol='http', sender_id=None):
        if not auth_key:
            raise ValueError('No auth_key specified. This is required for '
                             'calls against the Google-api.')
        if protocol not in self.ALLOWED_PROTOCOLS:
            raise ValueError('No protocol defined or not compatible.'
                             'Please use only allowed protocols ({})'
                             .format(self.ALLOWED_PROTOCOLS))
        self.auth_key = auth_key
        self.sender_id = sender_id
        self.headers = {'Authorization': 'key={}'.format(self.auth_key)}

    def send_message(self, to, priority='normal', ttl=None,
                     data=None, notification=None):
        if data and not isinstance(data, dict):
            raise AttributeError('Data can only be a dict.')
        if notification and not isinstance(notification, dict):
            raise AttributeError('Notification can only be a dict.')
        if not notification and not data:
            raise AttributeError('Data or notification needs to be filled.')
        data = {'to': to, 'data': data}
        if ttl:
            data.update({'time_to_live': ttl})
        return requests.post(url=self._http_google_message_api, data=data)

    def create_device_group(self, group_name, device_tokens):
        if not self.sender_id:
            raise ValueError('Sender-ID is required when using device-groups.')
        data = self._get_device_group_post_data(operation='create',
                                                device_tokens=device_tokens,
                                                group_name=group_name)
        headers = {'project_id': self.sender_id}
        headers.update(self.headers)
        return requests.post(url=self._http_google_notification_api,
                             json=data, headers=headers)

    def add_device_to_group(self, group_token, device_tokens):
        if not self.sender_id:
            raise ValueError('Sender-ID is required when using device-groups.')
        json_data = self._get_device_group_post_data(
            operation='add',
            device_tokens=device_tokens,
            group_token=group_token)
        headers = {'project_id': self.sender_id}
        headers.update(self.headers)
        return requests.post(url=self._http_google_notification_api,
                             json=json_data, headers=headers)

    def remove_device_from_group(self, group_token, device_tokens):
        if not self.sender_id:
            raise ValueError('Sender-ID is required when using device-groups.')
        json_data = self._get_device_group_post_data(
            operation='remove',
            device_tokens=device_tokens,
            group_token=group_token)
        headers = {'project_id': self.sender_id}
        headers.update(self.headers)
        return requests.post(url=self._http_google_notification_api,
                             json=json_data, headers=headers)

    def _get_device_group_post_data(self, operation, device_tokens,
                                    group_token=None, group_name=None):
        device_tokens = device_tokens \
            if isinstance(device_tokens, list) else [device_tokens]
        data = {'operation': operation,
                'registration_ids': device_tokens}
        if group_name:
            data.update({'notification_key_name': group_name})
        if group_token:
            data.update({'notification_key': group_token})
        if not group_token and not group_name:
            raise ValueError('No group-token or group-name specified.')
        return data
