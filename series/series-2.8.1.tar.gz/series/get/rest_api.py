from typing import Callable, Any

from flask import request

from series.logging import Logging
from golgi.config import configurable
from tek.tools import is_int

from tryp import Empty, Just, __, Map, List

from series.rest_api import RestApi as RestApiBase, route_decorator
from series.get.tvdb import Tvdb
from series.get.model.show import Show
from series.get import ReleaseMonitor


def error(msg, status=404):
    return dict(error=msg), status


@configurable(get=['rest_api_host', 'rest_api_port'])
class RestApi(RestApiBase, Tvdb):

    routes, route = route_decorator()

    def __init__(self, releases, shows, *a, **kw):
        RestApiBase.__init__(self, 'get')
        self._releases = releases
        self._shows = shows
        self._getd = Empty()

    def set_getd(self, daemon):
        self._getd = Just(daemon)

    def _no_release(self, _id):
        return error('No release with id {} found'.format(_id))

    def _release_map(self, _id, f: Callable[[ReleaseMonitor], Any]):
        release = self._releases.find_by_id(_id)
        if release:
            return f(release)
        else:
            return self._no_release(_id)

    def _release_foreach(self, _id, f: Callable[[ReleaseMonitor], Any]):
        def go(r):
            f(r)
            return 'ok'
        return self._release_map(_id, go)

    def _no_show(self, _id):
        return error('No show with id {} found'.format(_id))

    def _show_map(self, _id, f: Callable[[Show], Any]):
        show = self._shows.find_by_id(_id)
        if show:
            return f(show)
        else:
            return self._no_show(_id)

    @property
    def _no_getd(self):
        return error('SeriesGetD not running or connected to rest api', 500)

    @property
    def _json(self):
        return Map(request.get_json())

    @route('/release/explain_old')
    @route('/release/explain_old/<int:num>')
    def explain_old(self, num=5):
        return [r.explain_downloadable for r in self._releases[-num:]]

    @route('/release/<int:_id>/link', methods=['PUT'])
    def add_link(self, _id):
        url = self._json['url']
        if self._releases.add_link_by_id(_id, url):
            return 'Done'
        else:
            return self._no_release(_id)

    @route('/download/pending')
    def pending_downloads(self):
        releases = self._releases.pending_downloads
        dls = [(r.id, r.release.search_string) for r in releases]
        return dls

    @route('/release/<series>/<season>/<episode>/downloaded', methods=['PUT'])
    def mark_downloaded_metadata(self, series, season, episode):
        monitor = self._releases.find_by_metadata(series, season, episode)
        return self._mark_downloaded(monitor)

    @route('/release/<int:_id>/downloaded', methods=['PUT'])
    def mark_downloaded_id(self, _id):
        monitor = self._releases.find_by_id(_id)
        return self._mark_downloaded(monitor)

    @route('/release')
    def release_list(self):
        regex = self._json.get_or_else('regex', '')
        matches = self._releases.filter_episode_repr(regex)
        return [[str(monitor.id), str(monitor.release)] for monitor in matches]

    @route('/release_id')
    def id_by_metadata(self):
        data = self._json
        results = self._releases.find_by_metadata(data['series'],
                                                  data['season'],
                                                  data['episode'])
        return results.id if results else -1

    @route('/release/<series>/<season>/<episode>', methods=['POST'])
    def create_release(self, series, season, episode):
        if self._releases.find_by_metadata(series, season, episode):
            return 'Release already exists'
        else:
            self._releases.create(series, season, episode)
            return 'ok'

    @route('/release/<series>/<season>/<episode>', methods=['DELETE'])
    def delete_release(self, series, season, episode):
        if self._releases.find_by_metadata(series, season, episode):
            self._releases.delete(series, season, episode)
            return 'ok'
        else:
            return 'Release doesn\'t exist'

    @route('/release/<int:_id>', methods=['PUT'])
    def update_release(self, _id):
        if self._releases.find_by_id(_id):
            return self._releases.update_by_id(_id, **self._json).info
        else:
            return 'Release doesn\'t exist'

    @route('/season', methods=['POST'])
    def add_season(self):
        data = self._json
        if 'name' in data and 'season' in data and is_int(data['season']):
            name, season_name = data['name'], int(data['season'])
            show = self.tvdb.show(name)
            if show:
                season = self.tvdb.season(show.name, season_name)
                if season:
                    count = len(season)
                    self._releases.add_season(name, season_name, count)
                    return 'Done.'
                else:
                    return 'No such season: {} s{}'.format(name, season_name)
            else:
                return 'No such show: {}'.format(name)
        else:
            return 'Specify name and season in the parameters!'

    @route('/show', methods=['DELETE'])
    def delete_show(self):
        data = self._json
        if 'name' in data:
            name = data['name']
            if name.isdigit():
                self._shows.delete(int(name))
                return 'Done'
            else:
                show = self.tvdb.show(name)
                if show:
                    self._shows.delete_by_sid(show.showid)
                    return 'Done'
                else:
                    return 'No show with name "{}"'.format(name)
        else:
            return 'Specify show name in the parameters!'

    @route('/show', methods=['POST'])
    def add_show(self):
        data = self._json
        if 'name' in data:
            name = data['name']
            show = self.tvdb.show(name)
            if show:
                self._shows.add(name, show)
                return 'Done'
            else:
                return 'Adding show {} failed'.format(name)
        else:
            return 'Specify show name in the parameters!'

    @property
    def _target_shows(self):
        regex = self._json.get_or_else('regex', '')
        return self._shows.filter_by_regex(regex)

    @route('/show')
    def list_shows(self):
        return [[str(s.id), str(s.name)] for s in self._target_shows]

    def current_release(self, show):
        return self._releases.one(show.canonical_name, show.current_season,
                                  show.current_episode)

    def next_info(self, show):
        status = 0
        if show.has_next_episode:
            nepi = 'next episode: {}'.format(show.next_episode_date.date())
        else:
            nepi = 'no next episode'
            relinfo = None
        release = self.current_release(show)
        if release:
            if release.downloaded:
                status = 1
                air = release.release.airdate
                date = ' ({})'.format(air.date()) if air else ''
                enum = 'x'.join(map(str, release.enum))
                relinfo = 'release for {} downloaded{}'.format(enum, date)
            elif release.torrent:
                if release.torrent_valid():
                    valid = ''
                    status = 2
                else:
                    valid = 'in'
                    status = 3
                relinfo = 'release with {}valid torrent'.format(valid)
            else:
                relinfo = 'release without torrent'
        else:
            relinfo = 'no release yet'
        return [show.name, nepi, relinfo, status]

    @route('/show/info')
    def show_info(self):
        return list(map(self.next_info, self._target_shows))

    @route('/show/next')
    def next_shows(self):
        shows = [s for s in self._target_shows if s.has_next_episode]
        return list(map(self.next_info, shows))

    @route('/show/ready')
    def ready_shows(self):
        def has_release(show: Show):
            r = self.current_release(show)
            return (r is not None and
                    r.release.airdate == show.next_episode_date)
        shows = [s for s in self._target_shows if s.has_next_episode]
        valid = filter(has_release, shows)
        return list(map(self.next_info, valid))

    @route('/show/done')
    def done_shows(self):
        def done(show: Show):
            r = self.current_release(show)
            return r is not None and r.downloaded
        valid = filter(done, self._target_shows)
        return list(map(self.next_info, valid))

    def _mark_downloaded(self, monitor):
        if monitor:
            msg = 'Marking release "{}" as downloaded.'
            self.log.info(msg.format(monitor.release))
            self._releases.update_by_id(monitor.id, downloaded=True)
            self._releases.commit()
        return monitor is not None

    def _activate(self, _id):
        self._getd.foreach(__.activate_release(_id))

    @route('/release/<int:_id>/reset_torrent', methods=['PUT'])
    def reset_torrent(self, _id):
        def go(r):
            data = self._json
            self._releases.reset_torrent(_id)
            if 'link' in data and data['link']:
                self._releases.add_link_by_id(_id, data['link'])
            self._activate(_id)
        return self._release_foreach(_id, go)

    @route('/release/<int:_id>', methods=['GET'])
    def release_show(self, _id):
        release = self._releases.find_by_id(_id)
        return release.info if release is not None else self._no_release(_id)

    @route('/release/<int:_id>/activate', methods=['PUT'])
    def activate_release(self, _id):
        go = lambda r: self._activate(_id)
        return self._release_foreach(_id, go)

    @route('/release/<int:_id>/explain', methods=['GET'])
    def explain_release(self, _id):
        def go(release):
            services = self._json.get('services') / __.split(',') | ['all']
            s = List.wrap(services)
            r = List(release)
            return self._getd / __.explain_release(r, s) | self._no_getd
        return self._release_map(_id, go)

    @route('/show/<int:_id>/explain', methods=['GET'])
    def explain_show(self, _id):
        def go(show):
            services = self._json.get('services') / __.split(',') | ['all']
            s = List.wrap(services)
            r = List(show)
            return self._getd / __.explain_show(r, s) | self._no_getd
        return self._show_map(_id, go)

__all__ = ['RestApi']
