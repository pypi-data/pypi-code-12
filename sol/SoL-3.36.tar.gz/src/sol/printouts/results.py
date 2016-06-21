# -*- coding: utf-8 -*-
# :Project:   SoL -- Results printout
# :Created:   lun 13 giu 2016 11:46:23 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import CondPageBreak, Paragraph, Spacer, TableStyle
from reportlab.platypus.tables import Table

from ..i18n import translatable_string as _, gettext, translator
from ..models.errors import OperationAborted

from . import (
    caption_style,
    heading_style,
    normal_style,
    rank_width,
    scores_width,
    )
from .basic import TourneyPrintout
from .utils import ordinalp


class ResultsPrintout(TourneyPrintout):
    "Results of the last turn."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        args = super().getArgumentsFromRequest(session, request)
        t = translator(request)
        kw = request.params
        if 'turn' in kw:
            if kw['turn'] == 'all':
                args.append(None)
            else:
                try:
                    args.append(int(kw['turn']))
                except ValueError:
                    raise OperationAborted(
                        t(_('Invalid turn: $turn',
                            mapping=dict(turn=repr(kw['turn'])))))
        else:
            args.append(args[1].rankedturn)

        return args

    def __init__(self, output, locale, tourney, turn):
        super().__init__(output, locale, tourney, 1)
        self.turn = turn

    def getLitURL(self, request):
        if not request.host.startswith('localhost'):
            otherargs = {}
            if self.turn:
                otherargs['_query'] = {'turn': self.turn}
            return request.route_url('lit_tourney', guid=self.tourney.guid, **otherargs)

    def getSubTitle(self):
        if self.turn:
            if [m.final for m in self.tourney.matches if m.turn == self.turn][0]:
                return gettext('Results %s final round') % ordinalp(self.turn)
            else:
                return gettext('Results %s round') % ordinalp(self.turn)
        else:
            return gettext('All results')

    def getElements(self):
        yield from super().getElements()

        turn = self.turn

        results = [(m.turn, m.board,
                    m.caption(omit_competitor_decoration=True),
                    m.score1, m.score2, m.final)
                   for m in self.tourney.matches
                   if not turn or m.turn == turn]
        if not results:
            return

        results.sort()

        if turn:
            yield from self.getSingleTurnElements(results)
        else:
            yield from self.getAllTurnElements(results)

    def getSingleTurnElements(self, results):
        from reportlab.pdfbase.pdfmetrics import stringWidth

        slash_w = stringWidth('/', normal_style.fontName, normal_style.fontSize)

        rows = [(gettext('#'), gettext('Match'), '', gettext('Result'), '')]

        rows.extend([(board,
                      Paragraph(description, normal_style),
                      str(score1), '/', str(score2))
                     for (turn, board, description, score1, score2, final) in results])

        desc_width = self.doc.width/self.columns*0.9 - rank_width - scores_width*2 - slash_w
        yield Table(rows, (rank_width, desc_width, scores_width, slash_w, scores_width),
                    style=TableStyle([('ALIGN', (0,1), (0,-1), 'RIGHT'),
                                      ('ALIGN', (-3,0), (-3,-1), 'RIGHT'),
                                      ('ALIGN', (-2,0), (-2,-1), 'CENTER'),
                                      ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
                                      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                      ('FONT', (0,0), (-1,0), caption_style.fontName),
                                      ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                      ('LEADING', (0,0), (-1,0), caption_style.leading),
                                      ('SIZE', (0,1), (-1,-1), normal_style.fontSize),
                                      ('LEADING', (0,1), (-1,-1), normal_style.leading),
                                      ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.black)]))

    def getAllTurnElements(self, results):
        from itertools import groupby
        from operator import itemgetter

        key = itemgetter(0)
        for turn, res in groupby(results, key):
            yield CondPageBreak(4*cm)
            res = list(res)
            if res[0][5]:
                title = Paragraph(gettext('Results %s final round') % ordinalp(turn),
                                  heading_style)
            else:
                title = Paragraph(gettext('Results %s round') % ordinalp(turn), heading_style)
            yield title
            yield from self.getSingleTurnElements(res)
            yield Spacer(0, 0.4*cm)
