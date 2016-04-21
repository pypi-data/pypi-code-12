from django.test import TestCase
from django.contrib.auth.models import User
from likertblock.models import (
    Questionnaire, Question, Submission, Response)


class QuestionnaireTest(TestCase):
    def test_needs_submit(self):
        q = Questionnaire.objects.create()
        self.assertTrue(q.needs_submit())

    def test_clear_user_submissions(self):
        q = Questionnaire.objects.create()
        q.clear_user_submissions(None)


class QuestionTest(TestCase):
    def test_unicode(self):
        qn = Questionnaire.objects.create()
        q = Question.objects.create(questionnaire=qn, text="a question")
        self.assertEqual(str(q), "a question")


class SubmissionTest(TestCase):
    def test_unicode(self):
        qn = Questionnaire.objects.create()
        u = User.objects.create(username='foo')
        s = Submission.objects.create(user=u, questionnaire=qn)
        self.assertTrue("likert" in str(s))
        self.assertTrue("foo" in str(s))


class ResponseTest(TestCase):
    def test_likert_scale_label(self):
        qn = Questionnaire.objects.create()
        q = Question.objects.create(questionnaire=qn, text="a question")
        u = User.objects.create(username='foo')
        s = Submission.objects.create(user=u, questionnaire=qn)
        r = Response.objects.create(submission=s, question=q,
                                    value=0)
        self.assertEqual(r.likert_scale_label(), 'Strongly Disagree')
        r.value = 1
        r.save()
        self.assertEqual(r.likert_scale_label(), 'Somewhat Disagree')
        r.value = 2
        r.save()
        self.assertEqual(r.likert_scale_label(), 'Neutral')
        r.value = 3
        r.save()
        self.assertEqual(r.likert_scale_label(), 'Somewhat Agree')
        r.value = 4
        r.save()
        self.assertEqual(r.likert_scale_label(), 'Strongly Agree')
