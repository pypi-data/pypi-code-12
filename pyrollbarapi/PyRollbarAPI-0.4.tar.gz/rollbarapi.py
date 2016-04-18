from basegateway import APIGateway
import os

class PyAccountRollbarAPI(APIGateway):
  def __init__(self, account_read_token=os.environ.get('ROLLBAR_READ_TOKEN'), account_write_token=os.environ.get('ROLLBAR_WRITE_TOKEN')):
    APIGateway.__init__(self)
    self._host_url = 'https://api.rollbar.com/api/1'
    self._api = {
      'get_project': {
        'path': '/project/{id}',
        'method': 'GET',
        'params': {
          'access_token': account_read_token
        }
      },
      'get_project_access_tokens': {
        'path': '/project/{id}/access_tokens',
        'method': 'GET',
        'params': {
          'access_token': account_read_token
        }
      },
      'list_projects': {
        'path': '/projects',
        'method': 'GET',
        'params': {
          'access_token': account_read_token
        }
      }
    }
    self._common_params = {}
    self._common_headers = {}

  def get_project(self, project_id):
    return self.call('get_project', id=project_id)[0].get('result')

  def get_project_id_from_name(self, project_name):
    for project in (self.call('list_projects')[0]['result'] or []):
      if project['name'] == project_name:
        return project['id']
    return None

  def get_project_access_tokens(self, project_name, types=['read', 'write']):
    project_id = self.get_project_id_from_name(project_name)
    types = set(types)
    ret = {}
    for access_token in (self.call('get_project_access_tokens', id=project_id)[0].get('result') or []):
      name = access_token.get('name')
      if name in types:
        ret[name] = access_token.get('access_token')
        types.remove(name)
    if len(types):
      # Problem, TODO raise exception
      pass
    return ret

class PyRollbarAPI(APIGateway):
  def __init__(self, project_name):
    APIGateway.__init__(self)
    self._access_tokens = PyAccountRollbarAPI().get_project_access_tokens(project_name)
    self._host_url = 'https://api.rollbar.com/api/1'
    self._api = {
      'item_by_counter': {
        'path': '/item_by_counter/{counter}',
        'method': 'GET',
        'params': {
          'access_token': self._access_tokens['read']
        }
      },
      'get_item': {
        'path': '/item/{id}',
        'method': 'GET',
        'params': {
          'access_token': self._access_tokens['read']
        }
      },
      'patch_item': {
        'path': '/item/{id}',
        'method': 'PATCH',
        'params': {
          'access_token': self._access_tokens['write']
        }
      }
    }
    self._common_params = {}
    self._common_headers = {}

  def get_item(self, item_id):
    return self.call('get_item', id=item_id)[0].get('result')

  def get_item_from_counter(self, counter):
    return self.call('item_by_counter', counter=counter)[0].get('result')

  def resolve_item_from_counter(self, counter):
    item = self.get_item_from_counter(counter)
    if (item or {}).get('id') is not None:
      return self.resolve_item(item['id'])
    else:
      return False

  def resolve_item(self, item_id):
    return self.call('patch_item', id=item_id, data={"status": "resolved"})[1] == 200
