"""Views for the sprints app."""
from django.conf import settings
from django.views.generic import TemplateView
from django.utils.timezone import now

from . import trello_api
from . import freckle_api


class HomeView(TemplateView):
    template_name = 'sprints/home_view.html'


class BacklogView(TemplateView):
    template_name = 'sprints/backlog_view.html'

    def get_context_data(self, **kwargs):
        ctx = super(BacklogView, self).get_context_data(**kwargs)

        board = self.request.GET.get('board')
        rate = int(self.request.GET.get('rate') or 0)
        lists = self.request.GET.get('lists')
        selected_lists = []
        if lists:
            selected_lists = [
                int(list_) for list_ in
                self.request.GET.get('lists').split(',')]

        c = trello_api.TrelloClient(
            api_key=settings.TRELLO_DEVELOPER_KEY,
            api_secret=settings.TRELLO_DEVELOPER_SECRET,
            oauth_token=settings.TRELLO_OAUTH_TOKEN,
            oauth_secret=settings.TRELLO_OAUTH_TOKEN_SECRET,
            rate=rate,
        )

        tr_board = None
        tr_lists = []
        if board:
            tr_board = c.get_board(board)
            for list_index in selected_lists:
                tr_lists.append(c.get_list(tr_board, list_index))

        ctx.update({
            'board': tr_board,
            'lists': tr_lists,
        })
        return ctx


class SprintView(TemplateView):
    template_name = 'sprints/sprint_view.html'

    def get_context_data(self, **kwargs):
        ctx = super(SprintView, self).get_context_data(**kwargs)

        board = self.request.GET.get('board')
        project = self.request.GET.get('project')
        if project:
            project = int(project)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date') \
            or now().strftime('%Y-%m-%d')
        rate = int(self.request.GET.get('rate') or 0)

        c = trello_api.TrelloClient(
            api_key=settings.TRELLO_DEVELOPER_KEY,
            api_secret=settings.TRELLO_DEVELOPER_SECRET,
            oauth_token=settings.TRELLO_OAUTH_TOKEN,
            oauth_secret=settings.TRELLO_OAUTH_TOKEN_SECRET,
            rate=rate,
        )

        fr_entries = []
        fr_client = freckle_api.FreckleClient(
            'bitmazk', settings.FRECKLE_API_TOKEN, rate)
        if project and start_date and end_date:
            fr_entries = fr_client.get_entries(project, start_date, end_date)

        tr_board = None
        tr_cards = None
        if board:
            tr_board = c.get_board(board)
            tr_cards = c.get_cards(tr_board, fr_entries)

        ctx.update({
            'board': tr_board,
            'entries': fr_entries,
            'cards': tr_cards,
        })
        return ctx
