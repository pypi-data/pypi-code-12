from golgi.config import configurable
from series.logging import Logging

from series.api_client import ApiClient as Base


@configurable(library_client=['rest_api_port', 'rest_api_url'])
class ApiClient(Base):
    command = Base.command

    @command('series season episode', 'Create an episode with the ' +
             'supplied metadata')
    def create_episode(self, series, season, episode):
        data = dict(episode=episode)
        path = 'series/{}/seasons/{}/episodes'.format(series, season)
        response = self.post(path, body=data)
        self._info(response)
        return response

    @command('series season episode subfps', 'Set the episode\'s subfps')
    def subfps(self, series, season, episode, subfps):
        data = dict(subfps=subfps)
        path = 'series/{}/seasons/{}/episodes/{}'.format(series, season,
                                                         episode)
        response = self.put(path, body=data)
        self._info(response)
        return response

__all__ = ['ApiClient']
