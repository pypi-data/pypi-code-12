# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from pyramid.view import view_config
from pyramid.view import view_defaults

from kotti.views.util import template_api
from kotti_survey import _
from kotti_survey.resources import (
    Survey, Question, AnswerField, UserAnswer, UserSurvey
)
from kotti_survey.fanstatic import css_and_js
from kotti_survey.views import BaseView
from pyramid import httpexceptions as httpexc
from pyramid.renderers import render_to_response


@view_defaults(context=Survey, permission="view")
class SurveyView(BaseView):
    """View for Survey Content Type"""

    @view_config(name="view",
                 request_method='GET',
                 permission="view",
                 renderer='kotti_survey:templates/surveyview.pt')
    def view_survey(self):
        return {}

    @view_config(name='view',
                 request_method='POST',
                 permission="view",
                 renderer='kotti_survey:templates/resultview.pt')
    def save_answers(self):
        questions = self.context.children
        answers = {question.name: self.request.POST.getall(
            question.name) for question in questions}
        user_survey = self.context.save_answers(
            self.request, questions, answers)
        if not user_survey:
            return httpexc.HTTPFound(location=self.context.path)
        if self.context.redirect_url:
            redirect_url = self.context.redirect_url
        else:
            redirect_url = "{}/user-results".format(self.context.path)
        return httpexc.HTTPFound(location=redirect_url)

    @view_config(name='respondents',
                 permission="add",
                 renderer='kotti_survey:templates/respondents.pt')
    def list_users(self):
        user_surveys = UserSurvey.query.filter(
            UserSurvey.survey_id == self.context.id
        ).order_by(UserSurvey.date_completed.desc()).all()
        return {
            "user_surveys": user_surveys
        }

    @view_config(name='user-results',
                 permission="view",
                 renderer='kotti_survey:templates/resultview.pt')
    def show_answers(self):
        questions = self.context.children
        username = self.request.params.get(
            "username",
            self.request.user.name if self.request.user else ""
        )

        user_survey = UserSurvey.query.filter(
            UserSurvey.username == username,
            UserSurvey.survey_id == self.context.id
        ).order_by(UserSurvey.date_completed.desc()).first()

        answers = {}
        if user_survey:
            answer_dbs = UserAnswer.query.filter(
                UserAnswer.survey_id == self.context.id,
                UserAnswer.user_survey_id == user_survey.id
            ).all()
        for answer_db in answer_dbs:
            if answer_db.question_id in answers:
                answers[answer_db.question_id].append(answer_db.answer)
            else:
                answers[answer_db.question_id] = [answer_db.answer]
        return {
            'questions': questions,
            'answers': answers,
            'user_survey': user_survey
        }


@view_defaults(context=Question)
class QuestionView(BaseView):
    """View for Question Content Type"""

    @view_config(name="view", permission="view",
                 renderer='kotti_survey:templates/questionview.pt')
    def view_question(self):
        answers = self.context.values()
        return {
            'answers': answers,
        }


@view_defaults(context=AnswerField)
class AnswerView(BaseView):
    """View for Answer Content Type"""

    @view_config(name="view", permission="view",
                 renderer='kotti_quiz:templates/answerview.pt')
    def view_answer(self):
        return {}  # pragma: no cover
