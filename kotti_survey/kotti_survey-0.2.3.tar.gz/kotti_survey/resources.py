# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""
import datetime
import uuid
from kotti import Base, DBSession
from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    String,
    Boolean,
    DateTime
)
import user_agents
from zope.interface import implements
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSON, JSONB

from kotti_survey import _


def uuid_factory():
    return uuid.uuid4()


class Survey(Content):
    """Survey Content type."""
    implements(IDefaultWorkflow)

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    collect_user_info = Column(Boolean, default=False)
    redirect_url = Column(String)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)

    type_info = Content.type_info.copy(
        name=u'Survey',
        title=_(u'Survey'),
        add_view=u'add_survey',
        addable_to=[u'Document'],
    )

    def save_answers(self, request, questions, answers, username=None):
        browser_data = {
            "host": request.host,
            "client_ip": request.client_addr,
            "user_agent": request.user_agent,
        }

        if self.collect_user_info:
            if not username and not request.user:
                request.session.flash(
                    _("Please login or provide your username to continue."),
                    "warning"
                )
                return False
            survey = UserSurvey.query.filter(
                UserSurvey.survey_id == self.id,
                UserSurvey.username == (username or request.user.name)
            ).first()
            if survey:
                request.session.flash(
                    _("You have already done this survey."),
                    "warning"
                )
                return False
            survey = UserSurvey(
                browser_data=browser_data,
                survey_id=self.id,
                id=uuid_factory(),
                username=(username or request.user.name),
            )
        else:
            survey = UserSurvey(
                browser_data=browser_data,
                survey_id=self.id,
                id=uuid_factory()
            )
        if survey.save_answers(questions, answers):
            DBSession.add(survey)
            request.session.flash(
                _(u'Thank you for completing ${title}.',
                  mapping=dict(title=self.title)), 'success')
            return survey
        else:
            request.session.flash(
                _((u'Something went wrong, pleace check'
                   ' if all required fields are field out.')), 'danger')
            return False


class UserSurvey(Base):

    tablename = 'user_surveys'

    @declared_attr
    def __tablename__(cls):
        return cls.tablename

    id = Column(Unicode(100),
                primary_key=True, default=uuid_factory(), unique=True)
    browser_data = Column(JSON)
    date_completed = Column(DateTime, default=datetime.datetime.utcnow)
    survey_id = Column(
        Integer,
        ForeignKey('surveys.id', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True)
    username = Column(Unicode(100), primary_key=True, default=uuid_factory())
    answers = relationship("UserAnswer", cascade="save-update, merge, delete")

    @property
    def user_agent(self):
        if not hasattr(self, "_UserSurvey__user_agent"):
            try:
                self._user_agent = user_agents.parse(
                        self.browser_data["user_agent"]
                )
            except KeyError:
                self._user_agent = None
        return self._user_agent

    def save_answers(self, questions, answers):
        do_save = False
        for question in questions:
            if question.question_type == "text":
                if question.name in answers:
                    user_ans = answers[question.name][0]
                    if user_ans:
                        ans = UserAnswer(
                            answer=user_ans,
                            question_id=question.id,
                            survey_id=self.survey_id,
                            user_survey_id=self.id
                        )
                        do_save = True
                        self.answers.append(ans)
                    else:
                        do_save = False
            elif question.question_type == "radio":
                if question.name in answers:
                    user_ans = answers[question.name][0]
                    if user_ans:
                        ans = UserAnswer(
                            answer=user_ans,
                            question_id=question.id,
                            survey_id=self.survey_id,
                            user_survey_id=self.id
                        )
                        do_save = True
                        self.answers.append(ans)
                    else:
                        do_save = False
            elif question.question_type == "checkbox":
                if question.name in answers:
                    user_ans = answers[question.name]
                    if user_ans:
                        ans = UserAnswer(
                            answer=",".join(user_ans),
                            question_id=question.id,
                            is_multiple_choice=True,
                            survey_id=self.survey_id,
                            user_survey_id=self.id
                        )
                        do_save = True
                        self.answers.append(ans)
                    else:
                        do_save = False
            else:
                return False
            if not do_save:
                return False
        return do_save


class Question(Content):
    """Question Content type."""
    tablename = 'survey_questions'

    @declared_attr
    def __tablename__(cls):
        return cls.tablename

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    question_type = Column(String())

    # change the type info to your needs
    type_info = Content.type_info.copy(
        name=u'Question',
        title=_(u'Question'),
        add_view=u'add_question',
        addable_to=[u'Survey'],
        )


class AnswerField(Content):
    """Answer Content type."""
    tablename = 'survey_fields'

    @declared_attr
    def __tablename__(cls):
        return cls.tablename

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)

    type_info = Content.type_info.copy(
        name=u'Answer',
        title=_(u'Answer'),
        add_view=u'add_answer',
        addable_to=[u'Question'],
        )


class UserAnswer(Base):
    tablename = 'survey_answers'

    @declared_attr
    def __tablename__(cls):
        return cls.tablename

    is_multiple_choice = Column(Boolean, default=False)
    question_id = Column(
        Integer,
        ForeignKey('survey_questions.id', onupdate="CASCADE",
                   ondelete="CASCADE"),
        primary_key=True)
    survey_id = Column(
        Integer,
        ForeignKey('surveys.id', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True)
    user_survey_id = Column(
        Unicode(100),
        ForeignKey('user_surveys.id', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    answer = Column(String)
