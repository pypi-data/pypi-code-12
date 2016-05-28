import re

from tek.config import configurable
from tek.tools import find
from tek import logger
from tek.io.terminal import terminal as term, ColorString

from series.api_client import ApiClient as Base


def is_error(response):
    return isinstance(response, dict) and 'error' in response


@configurable(get_client=['rest_api_port', 'rest_api_url'])
class ApiClient(Base):
    command = Base.command

    @command('url (id || series season episode)', 'Add the url to the ' +
             'specified release\'s links')
    def add_link(self, url, series=None, season=None, episode=None):
        if episode is not None:
            data = dict(series=series, season=season, episode=episode)
            _id = self.get('release_id', body=data)
        elif isinstance(series, int):
            _id = series
        else:
            dls = self.get('download/pending')
            release = find(lambda r: re.search(r[1], url, re.I), dls)
            _id = release[0] if release else -1
        if _id != -1:
            response = self.put('release/{}/link'.format(_id),
                                body=dict(url=url))
            if not is_error(response):
                logger.info(response)
            else:
                _id = -1
        else:
            logger.error('No matching release found!')
        return _id

    @command('count', 'Describe the state of the latest `count` releases,'
             ' default 5')
    def explain(self, count=5):
        output = self.get('release/explain/{}'.format(count))
        for line in output:
            logger.info(line)
        return output

    @command('id', 'Set the \'downloaded\' flag for the specified release')
    def mark_downloaded(self, _id):
        return self._downloaded_flag(_id, True)

    @command('id', 'Unset the \'downloaded\' flag for the specified release')
    def mark_not_downloaded(self, _id):
        return self._downloaded_flag(_id, False)

    def _downloaded_flag(self, _id, value):
        success = self.put('release/{}'.format(_id),
                           body=dict(downloaded=value, archived=value))
        if success:
            logger.info('Success!')
        else:
            logger.error('Release not found!')
        return bool(success)

    @command('[regex]', 'Display id, name, season and episode for all ' +
             'releases matching the regex (default all)')
    def list(self, regex=''):
        matches = self.get('release', body=dict(regex=regex))
        if matches:
            text = 'id #{}: {}'
            for id, description in matches:
                logger.info(text.format(id, description))
        else:
            logger.info('No matching release found.')
        return matches

    @command('series season episode', 'Create an empty release with the ' +
             'supplied metadata')
    def create_release(self, series, season, episode):
        response = self.post('release/{}/{}/{}'.format(series, season,
                                                       episode))
        logger.info(response)
        return response

    @command('series season episode', 'Delete the release matching the ' +
             'supplied metadata')
    def delete_release(self, series, season, episode):
        response = self.delete('release/{}/{}/{}'.format(series, season,
                                                         episode))
        logger.info(response)
        return response

    @command('series season', 'Add the specified season of series to the db')
    def add_season(self, name, season):
        response = self.post('season', body=dict(name=name, season=season))
        logger.info(response)
        return response

    @command('name', 'Add the specified show')
    def add_show(self, name):
        response = self.post('show', body=dict(name=name))
        logger.info(response)
        return response

    @command('canonical_name|id', 'Delete the specified show')
    def delete_show(self, name):
        response = self.delete('show', body=dict(name=name))
        logger.info(response)
        return response

    @command('[regex]', 'List show names matching the regex')
    def list_shows(self, regex=''):
        matches = self.get('show', body=dict(regex=regex))
        if matches:
            text = 'id #{}: {}'
            for id, description in matches:
                logger.info(text.format(id, description))
        else:
            logger.info('No matching show found.')
        return matches

    def print_shows(self, shows):
        colors = {
            0: term.blue,
            1: term.green,
            2: term.yellow,
            3: term.red,
        }
        if shows:
            for name, nepi, rel, status in shows:
                term.push([ColorString('>> ', term.red),
                           ColorString(name, term.bold)])
                term.push([ColorString(' | ', term.green), nepi])
                if rel:
                    col = colors.get(status, term.black)
                    term.push([ColorString(' | ', term.green),
                               ColorString(rel, col)])
                logger.info('')
        else:
            logger.info('No matching show found.')
        return shows

    @command('[regex]', 'Extended info for shows matching regex')
    def shows(self, regex=''):
        return self.print_shows(self.get('show/info', body=dict(regex=regex)))

    @command('[regex]', 'List upcoming releases for shows matching regex')
    def next(self, regex=''):
        return self.print_shows(self.get('show/next', body=dict(regex=regex)))

    @command('[regex]', 'List current releases for shows matching regex')
    def ready(self, regex=''):
        return self.print_shows(self.get('show/ready', body=dict(regex=regex)))

    @command('[regex]', 'List downloaded releases for shows matching regex')
    def done(self, regex=''):
        return self.print_shows(self.get('show/done', body=dict(regex=regex)))

__all__ = ['ApiClient']
