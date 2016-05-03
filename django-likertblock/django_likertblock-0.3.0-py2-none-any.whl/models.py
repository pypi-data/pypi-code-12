from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from pagetree.models import PageBlock


class Questionnaire(models.Model):
    pageblocks = GenericRelation(PageBlock)
    description = models.TextField(blank=True)

    display_name = "Likert"
    template_file = "likertblock/likertblock.html"
    exportable = True
    importable = True

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return True

    def submit(self, user, data):
        s = Submission.objects.create(questionnaire=self, user=user)
        for k in data.keys():
            if k.startswith('likert-question'):
                qid = int(k[len('likert-question'):])
                question = Question.objects.get(id=qid)
                Response.objects.create(
                    submission=s,
                    question=question,
                    value=data[k])

    def redirect_to_self_on_submit(self):
        return True

    def unlocked(self, user):
        return Submission.objects.filter(
            questionnaire=self, user=user).count() > 0

    def edit_form(self):
        class EditForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea(),
                                          initial=self.description)
            alt_text = ("<a href=\"" + reverse("edit-questionnaire",
                                               args=[self.id])
                        + "\">manage questions</a>")
        return EditForm()

    def update_questions_order(self, question_ids):
        self.set_question_order(question_ids)

    def clear_user_submissions(self, user):
        Submission.objects.filter(user=user, questionnaire=self).delete()

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea())
        return AddForm()

    @classmethod
    def create(self, request):
        return Questionnaire.objects.create(
            description=request.POST.get('description', ''))

    @classmethod
    def create_from_dict(self, d):
        q = Questionnaire.objects.create(
            description=d.get('description', ''))
        q.import_from_dict(d)
        return q

    def edit(self, vals, files):
        self.description = vals.get('description', '')
        self.save()

    def add_question_form(self, request=None):
        return QuestionForm(request)

    def as_dict(self):
        return dict(
            description=self.description,
            questions=[q.as_dict() for q in self.question_set.all()]
        )

    def import_from_dict(self, d):
        self.description = d['description']
        self.save()
        self.submission_set.all().delete()
        self.question_set.all().delete()
        for q in d['questions']:
            Question.objects.create(
                questionnaire=self,
                text=q['text'])

    def summary_render(self):
        if len(self.description) < 61:
            return self.description
        else:
            return self.description[:61] + "..."


class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire)
    text = models.TextField(blank=True)

    class Meta:
        order_with_respect_to = 'questionnaire'

    def __unicode__(self):
        return self.text

    def display_number(self):
        return self._order + 1

    def edit_form(self, request=None):
        return QuestionForm(request, instance=self)

    def user_responses(self, user):
        qs = Submission.objects.filter(
            user=user,
            questionnaire=self.questionnaire).order_by("-submitted")
        if len(qs) == 0:
            return Response.objects.none()
        else:
            submission = qs[0]
            return Response.objects.filter(
                question=self,
                submission=submission)

    def as_dict(self):
        return dict(text=self.text)


class Submission(models.Model):
    questionnaire = models.ForeignKey(Questionnaire)
    user = models.ForeignKey(User, related_name='likert_submission')
    submitted = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "likert %d submission by %s at %s" % (
            self.questionnaire.id, unicode(self.user), self.submitted)


class Response(models.Model):
    question = models.ForeignKey(Question)
    submission = models.ForeignKey(Submission)
    value = models.IntegerField(default=0)

    def likert_scale_label(self):
        return [
            'Strongly Disagree',
            'Somewhat Disagree',
            'Neutral',
            'Somewhat Agree',
            'Strongly Agree',
        ][self.value]


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ("questionnaire",)
        fields = ('text',)
