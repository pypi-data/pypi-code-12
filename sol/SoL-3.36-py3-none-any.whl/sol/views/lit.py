# -*- coding: utf-8 -*-
# :Project:   SoL -- Light user interface controller
# :Created:   ven 12 dic 2008 09:18:37 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008, 2009, 2010, 2013, 2014, 2016 Lele Gaifax
#

from datetime import date
from functools import wraps
import logging

from babel.numbers import format_decimal

from markupsafe import escape

from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPMovedPermanently,
    HTTPNotFound,
    )
from pyramid.view import view_config

from sqlalchemy import distinct, func, select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import or_, exists

from . import get_request_logger
from ..i18n import translatable_string as _, translator, gettext, ngettext
from ..models import (
    DBSession,
    Championship,
    Club,
    MergedPlayer,
    Player,
    Rating,
    Tourney,
    )


logger = logging.getLogger(__name__)


@view_config(route_name="lit", renderer="lit/index.mako")
def index(request):
    from collections import defaultdict

    sess = DBSession()

    clubs = sess.query(Club).filter(or_(exists().where(Player.idclub == Club.idclub),
                                        exists().where(Championship.idclub == Club.idclub))).all()
    nclubs = len(clubs)
    nfeds = len([c for c in clubs if c.isfederation])
    ntourneys = sess.query(func.count(Tourney.idtourney)).scalar()
    nchampionships = sess.query(func.count(Championship.idchampionship)).scalar()
    nplayers = sess.query(func.count(Player.idplayer)).scalar()
    npcountries = sess.query(func.count(distinct(Player.nationality))) \
                      .filter(Player.nationality != None).scalar()
    nratings = sess.query(func.count(Rating.idrating)).scalar()
    bycountry = defaultdict(list)
    for club in clubs:
        bycountry[(club.country, club.nationality)].append(club)

    return {
        "_": gettext,
        "clubsbycountry": bycountry,
        "nccountries": len(bycountry),
        "nchampionships": nchampionships,
        "nclubs": nclubs,
        "nfederations": nfeds,
        "ngettext": ngettext,
        "npcountries": npcountries,
        "nplayers": nplayers,
        "nratings": nratings,
        "ntourneys": ntourneys,
        "request": request,
        "session": sess,
        "today": date.today(),
        "version": request.registry.settings['desktop.version'],
    }


def _build_template_data(request, session, entity, **kwargs):
    data = {
        '_': gettext,
        'escape': escape,
        'entity': entity,
        'ngettext': ngettext,
        'request': request,
        'session': session,
        'today': date.today(),
        'version': request.registry.settings['desktop.version'],
    }
    data.update(kwargs)
    return data


def resolve_guids(*pairs):
    def decorator(func):
        @wraps(func)
        def wrapper(request):
            t = translator(request)
            params = request.matchdict
            sess = DBSession()
            entities = []
            # Take paired arguments two-by-two, inline simpler version of
            # itertools::grouper recipe
            ipairs = iter(pairs)
            for pname, iclass in zip(ipairs, ipairs):
                try:
                    guid = params[pname]
                except KeyError:
                    msg = "Missing required argument: %s" % pname
                    get_request_logger(request, logger).warn(msg)
                    raise HTTPBadRequest(msg)
                try:
                    instance = sess.query(iclass).filter_by(guid=guid).one()
                except NoResultFound:
                    if iclass is Player:
                        try:
                            merged = sess.query(MergedPlayer).filter_by(guid=guid).one()
                        except NoResultFound:
                            get_request_logger(request, logger).warn(
                                "Couldn't create page: no %s with guid %s",
                                iclass.__name__.lower(), guid)
                            msg = t(_('No $entity with guid $guid'),
                                    mapping=dict(entity=iclass.__name__.lower(), guid=guid))
                            raise HTTPNotFound(msg)
                        entities.append((guid, merged.player.guid))
                    else:
                        get_request_logger(request, logger).warn(
                            "Couldn't create page: no %s with guid %s",
                            iclass.__name__.lower(), guid)
                        msg = t(_('No $entity with guid $guid'),
                                mapping=dict(entity=iclass.__name__.lower(), guid=guid))
                        raise HTTPNotFound(msg)
                else:
                    entities.append(instance)
            return func(request, sess, entities)
        return wrapper
    return decorator


@view_config(route_name="lit_championship", renderer="lit/championship.mako")
@resolve_guids('guid', Championship)
def championship(request, session, entities):
    cship = entities[0]
    data = _build_template_data(request, session, cship)

    if cship.closed:
        request.response.cache_control.public = True
        request.response.cache_control.max_age = 60*60*24*365

    if cship.prizes != 'centesimal':
        data["format_prize"] = lambda p: format_decimal(p, '###0',
                                                   getattr(request, '_LOCALE_', 'en'))
    else:
        data["format_prize"] = lambda p: format_decimal(p, '###0.00',
                                                   getattr(request, '_LOCALE_', 'en'))

    return data


@view_config(route_name="lit_club", renderer="lit/club.mako")
@resolve_guids('guid', Club)
def club(request, session, entities):
    return _build_template_data(request, session, entities[0])


@view_config(route_name="lit_club_players", renderer="lit/club_players.mako")
@resolve_guids('guid', Club)
def club_players(request, session, entities):
    from itertools import groupby

    club = entities[0]
    query = session.query(Player) \
                   .filter(or_(Player.idclub == club.idclub,
                               Player.idfederation == club.idclub)) \
                   .order_by(Player.lastname, Player.firstname)
    players = groupby(query, lambda player: player.lastname[0])
    return _build_template_data(request, session, club, players=players)


@view_config(route_name="lit_player", renderer="lit/player.mako")
@resolve_guids('guid', Player)
def player(request, session, entities):
    player = entities[0]
    if isinstance(player, tuple):
        old_guid, new_guid = player
        get_request_logger(request, logger).debug(
            "Redirecting from player %s to %s", old_guid, new_guid)
        raise HTTPMovedPermanently(
            request.route_path('lit_player', guid=new_guid))
    else:
        data = _build_template_data(request, session, player)
        data["format_prize"] = lambda p: format_decimal(p, '###0.00',
                                                   getattr(request, '_LOCALE_', 'en'))
        return data


@view_config(route_name="lit_player_opponent", renderer="lit/player_opponent.mako")
@resolve_guids('guid', Player, 'opponent', Player)
def opponent(request, session, entities):
    player = entities[0]
    opponent = entities[1]
    if isinstance(player, tuple) or isinstance(opponent, tuple):
        if isinstance(player, tuple):
            p_old_guid, p_new_guid = player
        else:
            p_old_guid = p_new_guid = player.guid
        if isinstance(opponent, tuple):
            o_old_guid, o_new_guid = opponent
        else:
            o_old_guid = o_new_guid = opponent.guid
        get_request_logger(request, logger).debug(
            "Redirecting from player %s to %s and from opponent %s to %s",
            p_old_guid, p_new_guid, o_old_guid, o_new_guid)
        raise HTTPMovedPermanently(
            request.route_path('lit_player_opponent', guid=p_new_guid, opponent=o_new_guid))
    else:
        return _build_template_data(request, session, player, opponent=opponent)


@view_config(route_name="lit_player_matches", renderer="lit/player_matches.mako")
@resolve_guids('guid', Player)
def matches(request, session, entities):
    player = entities[0]
    if isinstance(player, tuple):
        old_guid, new_guid = player
        get_request_logger(request, logger).debug(
            "Redirecting from player %s to %s", old_guid, new_guid)
        raise HTTPMovedPermanently(
            request.route_path('lit_player', guid=new_guid))
    else:
        return _build_template_data(request, session, player)


@view_config(route_name="lit_players", renderer="lit/players.mako")
def players(request):
    from itertools import groupby
    from operator import itemgetter
    from gettext import translation
    from pycountry import LOCALES_DIR, countries

    lname = getattr(request, 'locale_name', 'en')
    try:
        t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
    except IOError:
        t = lambda x: x

    sess = DBSession()
    pt = Player.__table__
    query = sess.execute(select([func.substr(pt.c.lastname, 1, 1),
                                 pt.c.nationality,
                                 func.count()]).group_by(func.substr(pt.c.lastname, 1, 1),
                                                         pt.c.nationality))
    index = []
    for letter, countsbycountry in groupby(query, itemgetter(0)):
        bycountry = []
        for country in countsbycountry:
            ccode = country[1]
            if ccode:
                if ccode == 'eur':
                    cname = translator(request)(_('Europe'))
                else:
                    cname = t(countries.get(alpha3=ccode).name)
            else:
                cname = translator(request)(_('Unspecified country'))

            bycountry.append(dict(code=ccode, country=cname, count=country[2]))
        bycountry.sort(key=itemgetter('country'))
        index.append((letter, bycountry))

    return {
        '_': gettext,
        'ngettext': ngettext,
        'today': date.today(),
        'version': request.registry.settings['desktop.version'],
        'index': index,
        'request': request,
    }


@view_config(route_name="lit_players_list", renderer="lit/players_list.mako")
def players_list(request):
    from gettext import translation
    from pycountry import LOCALES_DIR, countries

    lname = getattr(request, 'locale_name', 'en')
    try:
        t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
    except IOError:
        t = lambda x: x

    letter = request.matchdict['letter']
    ccode = request.matchdict['country']

    if ccode == 'None':
        ccode = None

    if ccode:
        if ccode == 'eur':
            cname = translator(request)(_('Europe'))
        else:
            cname = t(countries.get(alpha3=ccode).name)
    else:
        cname = translator(request)(_('Unspecified country'))

    sess = DBSession()
    players = sess.query(Player) \
                  .filter(func.substr(Player.lastname, 1, 1) == letter,
                          Player.nationality == ccode) \
                  .order_by(Player.lastname, Player.firstname)

    return {
        '_': gettext,
        'code': ccode,
        'country': cname,
        'letter': letter,
        'ngettext': ngettext,
        'players': players,
        'request': request,
        'today': date.today(),
        'version': request.registry.settings['desktop.version'],
    }


@view_config(route_name="lit_rating", renderer="lit/rating.mako")
@resolve_guids('guid', Rating)
def rating(request, session, entities):
    rating = entities[0]
    tt = Tourney.__table__
    ntourneys = session.execute(select([func.count(tt.c.idtourney)],
                                       tt.c.idrating==rating.idrating)).first()[0]
    return _build_template_data(request, session, rating, ntourneys=ntourneys)


@view_config(route_name="lit_tourney", renderer="lit/tourney.mako")
@resolve_guids('guid', Tourney)
def tourney(request, session, entities):
    t = translator(request)

    tourney = entities[0]
    turn = request.params.get('turn')
    if turn is not None:
        try:
            turn = int(turn)
        except ValueError:
            get_request_logger(request, logger).warn(
                "Couldn't create page: argument “turn” is not an integer: %r", turn)
            e = t(_('Invalid turn: $turn'), mapping=dict(turn=repr(turn)))
            raise HTTPBadRequest(str(e))

    data = _build_template_data(request, session, tourney, turn=turn,
                                player=request.params.get('player'))

    if tourney.championship.prizes != 'centesimal':
        data["format_prize"] = lambda p: format_decimal(p, '###0',
                                                   getattr(request, '_LOCALE_', 'en'))
    else:
        data["format_prize"] = lambda p: format_decimal(p, '###0.00',
                                                   getattr(request, '_LOCALE_', 'en'))

    if tourney.prized:
        request.response.cache_control.public = True
        request.response.cache_control.max_age = 60*60*24*365

    return data


@view_config(route_name="lit_latest", renderer="lit/latest.mako")
def latest(request):
    t = translator(request)

    n = request.params.get('n')
    if n is not None:
        try:
            n = int(n)
        except ValueError:
            get_request_logger(request, logger).warn(
                "Couldn't create page: argument “n” is not an integer: %r", n)
            e = t(_('Invalid number of tourneys: $n'), mapping=dict(n=repr(n)))
            raise HTTPBadRequest(str(e))
    else:
        n = 20

    sess = DBSession()
    tourneys = sess.query(Tourney).filter_by(prized=True).order_by(Tourney.date.desc())[:n]

    return {
        '_': gettext,
        'escape': escape,
        'n': len(tourneys),
        'ngettext': ngettext,
        'request': request,
        'session': DBSession(),
        'today': date.today(),
        'tourneys': tourneys,
        'version': request.registry.settings['desktop.version'],
    }
