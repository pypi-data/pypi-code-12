from django.conf.urls import patterns
from .views import (
    EditQuestionnaireView, DeleteQuestionView, ReorderQuestionsView,
    AddQuestionToQuestionnaireView, EditQuestionView,
)

urlpatterns = patterns(
    'likertblock.views',
    (r'^edit_questionnaire/(?P<pk>\d+)/$', EditQuestionnaireView.as_view(),
     {}, 'edit-questionnaire'),
    (r'^edit_questionnaire/(?P<pk>\d+)/add_question/$',
     AddQuestionToQuestionnaireView.as_view(), {},
     'add-question-to-questionnaire'),
    (r'^edit_question/(?P<pk>\d+)/$', EditQuestionView.as_view(), {},
     'likert-edit-question'),
    (r'^delete_question/(?P<pk>\d+)/$', DeleteQuestionView.as_view(), {},
     'likert-delete-question'),
    (r'^reorder_questions/(?P<pk>\d+)/$', ReorderQuestionsView.as_view(), {},
     'likert-reorder-questions'),
)
