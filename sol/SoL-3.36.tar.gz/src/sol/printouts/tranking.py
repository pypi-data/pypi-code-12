# -*- coding: utf-8 -*-
# :Project:   SoL -- Ranking printout
# :Created:   lun 13 giu 2016 11:41:01 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, TableStyle
from reportlab.platypus.tables import Table

from ..i18n import translatable_string as _, gettext, ngettext, translator
from ..models.errors import OperationAborted

from . import (
    caption_style,
    cardinfo_style,
    cardname_style,
    heading_style,
    normal_style,
    prizes_width,
    rank_width,
    scores_width,
    )
from .basic import TourneyPrintout
from .utils import ordinal


class TourneyRankingPrintout(TourneyPrintout):
    "Current ranking of a tourney."

    leftMargin=0.1*cm
    rightMargin=0.1*cm

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        args = super().getArgumentsFromRequest(session, request)
        t = translator(request)
        kw = request.params
        if 'turn' in kw:
            try:
                args.append(int(kw['turn']))
            except ValueError:
                raise OperationAborted(
                    t(_('Invalid turn: $turn',
                        mapping=dict(turn=repr(kw['turn'])))))
        return args

    def __init__(self, output, locale, tourney, turn=None):
        super().__init__(output, locale, tourney, 1)
        self.turn = turn

    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Ranking after %s round') % ordinal(self.turn)
        else:
            if self.tourney.prized:
                return gettext('Final ranking')
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Ranking after %s round') % ordinal(rt)
                else:
                    return gettext('Initial ranking')

    def getFinalElements(self):
        from collections import defaultdict

        finalmatches = [m for m in self.tourney.matches if m.final]
        results = defaultdict(list)
        order = []

        for match in finalmatches:
            caption = gettext('$comp1 vs. $comp2', mapping=dict(
                comp1=match.competitor1, comp2=match.competitor2))
            if caption not in results:
                order.append(caption)
            results[caption].append('%d/%d' % (match.score1, match.score2))

        for i, caption in enumerate(order):
            if i == 0:
                yield Paragraph(ngettext('Result of the final for the 1st/2nd place',
                                         'Results of the final for the 1st/2nd place',
                                         len(results[caption])), heading_style)
            else:
                yield Paragraph(ngettext('Result of the final for the 3rd/4th place',
                                         'Results of the final for the 3rd/4th place',
                                         len(results[caption])), heading_style)
            yield Paragraph(caption, cardname_style)
            yield Paragraph(', '.join(results[caption]), cardinfo_style)
            yield Spacer(0, 0.6*cm)

    def getElements(self):
        yield from super().getElements()

        def player_caption(player, html, localized, css_class=None):
            caption = player.caption(html=html, localized=localized, css_class=css_class)
            if player.club:
                caption += "<font size=6> %s</font>" % player.club
            return caption

        if self.turn is not None:
            ranking = [(i, c.caption(player_caption=player_caption), c.nationality,
                        r.points, r.bucholz, r.netscore, 0)
                       for i, (c, r) in enumerate(self.tourney.computeRanking(self.turn), 1)]
        else:
            ranking = [(i, c.caption(player_caption=player_caption), c.nationality,
                        c.points, c.bucholz, c.netscore, self.format_prize(c.prize))
                       for i, c in enumerate(self.tourney.ranking, 1)]

            if self.tourney.finals and self.tourney.prized:
                yield from self.getFinalElements()

        if not ranking: # pragma: no cover
            return

        is_intl = len(set(r[2] for r in ranking)) > 1

        if self.tourney.championship.playersperteam > 1:
            caption = gettext('Team')
        else:
            caption = gettext('Player')

        if self.tourney.prized and self.turn is None:
            if self.tourney.championship.prizes == 'asis':
                npointcols = 3
                rows = [('#',
                         '',
                         caption,
                         gettext('Pts'),
                         gettext('Bch'),
                         gettext('Net')) if is_intl
                        else ('#',
                              caption,
                              gettext('Pts'),
                              gettext('Bch'),
                              gettext('Net'))]
                rows.extend((rank,
                             country,
                             Paragraph(description, normal_style),
                             points,
                             bucholz,
                             netscore) if is_intl
                            else (rank,
                                  Paragraph(description, normal_style),
                                  points,
                                  bucholz,
                                  netscore)
                            for (rank, description, country,
                                 points, bucholz, netscore, prize) in ranking)
                desc_width = (self.doc.width - rank_width - scores_width*4 -
                              (scores_width if is_intl else 0))
                widths = (
                    rank_width, scores_width, desc_width,
                    scores_width, scores_width,
                    scores_width
                ) if is_intl else (
                    rank_width, desc_width,
                    scores_width, scores_width,
                    scores_width)
            else:
                npointcols = 4
                rows = [('#',
                         '',
                         caption,
                         gettext('Pts'),
                         gettext('Bch'),
                         gettext('Net'),
                         gettext('Prz')) if is_intl
                        else ('#',
                              caption,
                              gettext('Pts'),
                              gettext('Bch'),
                              gettext('Net'),
                              gettext('Prz'))]
                rows.extend((rank,
                             country,
                             Paragraph(description, normal_style),
                             points,
                             bucholz,
                             netscore,
                             prize) if is_intl
                            else (rank,
                                  Paragraph(description, normal_style),
                                  points,
                                  bucholz,
                                  netscore,
                                  prize)
                            for (rank, description, country,
                                 points, bucholz, netscore, prize) in ranking)
                desc_width = (self.doc.width - rank_width - scores_width*4 - prizes_width -
                              (scores_width if is_intl else 0))
                widths = (
                    rank_width, scores_width, desc_width,
                    scores_width, scores_width,
                    scores_width, prizes_width
                ) if is_intl else (
                    rank_width, desc_width,
                    scores_width, scores_width,
                    scores_width, prizes_width)

            yield Table(rows, widths,
                        style=TableStyle([('ALIGN', (0,0), (0,-1), 'RIGHT'),
                                          ('ALIGN', (-npointcols,0), (-1,-1), 'RIGHT'),
                                          ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                          ('FONT', (0,0), (-1,0), caption_style.fontName),
                                          ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                          ('LEADING', (0,0), (-1,0), caption_style.leading),
                                          ('SIZE', (0,1), (0,-1), normal_style.fontSize),
                                          ('LEADING', (0,1), (0,-1), normal_style.leading),
                                          ('SIZE', (-npointcols,1), (-1,-1), normal_style.fontSize),
                                          ('LEADING', (-npointcols,1), (-1,-1), normal_style.leading),
                                          ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)]))
        else:
            rows = [('#',
                     '',
                     caption,
                     gettext('Pts'),
                     gettext('Bch'),
                     gettext('Net')) if is_intl
                    else ('#',
                          caption,
                          gettext('Pts'),
                          gettext('Bch'),
                          gettext('Net'))]
            rows.extend([(rank,
                          country,
                          Paragraph(description, normal_style),
                          points,
                          bucholz,
                          netscore) if is_intl
                         else (rank,
                               Paragraph(description, normal_style),
                               points,
                               bucholz,
                               netscore)
                         for (rank, description, country, points,
                              bucholz, netscore, prize) in ranking])
            desc_width = (self.doc.width/self.columns*0.9 - rank_width -
                          scores_width*3 -
                          (scores_width if is_intl else 0))
            yield Table(rows,
                        (rank_width, scores_width, desc_width,
                         scores_width, scores_width, scores_width) if is_intl
                        else (rank_width, desc_width,
                              scores_width, scores_width, scores_width),
                        style=TableStyle([('ALIGN', (0,0), (0,-1), 'RIGHT'),
                                          ('ALIGN', (-3,0), (-1,-1), 'RIGHT'),
                                          ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                          ('FONT', (0,0), (-1,0), caption_style.fontName),
                                          ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                          ('LEADING', (0,0), (-1,0), caption_style.leading),
                                          ('SIZE', (0,1), (0,-1), normal_style.fontSize),
                                          ('LEADING', (0,1), (0,-1), normal_style.leading),
                                          ('SIZE', (-3,1), (-1,-1), normal_style.fontSize),
                                          ('LEADING', (-3,1), (-1,-1), normal_style.leading),
                                          ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)]))
