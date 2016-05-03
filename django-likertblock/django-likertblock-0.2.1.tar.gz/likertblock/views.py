from .models import Questionnaire, Question
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView


class EditQuestionnaireView(DetailView):
    model = Questionnaire


class DeleteQuestionView(DeleteView):
    model = Question

    def get_success_url(self):
        questionnaire = self.object.questionnaire
        return reverse("edit-questionnaire", args=[questionnaire.id])


class ReorderQuestionsView(View):
    def post(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        keys = request.GET.keys()
        question_keys = [int(k[len('question_'):]) for k in keys
                         if k.startswith('question_')]
        question_keys.sort()
        questions = [int(request.GET['question_' + str(k)])
                     for k in question_keys]
        questionnaire.update_questions_order(questions)
        return HttpResponse("ok")


class AddQuestionToQuestionnaireView(View):
    def post(self, request, pk):
        questionnaire = get_object_or_404(Questionnaire, pk=pk)
        form = questionnaire.add_question_form(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.questionnaire = questionnaire
            question.save()
        return HttpResponseRedirect(
            reverse("edit-questionnaire", args=[questionnaire.id]))


class EditQuestionView(View):
    template_name = 'likertblock/edit_question.html'

    def get_object(self, pk):
        return get_object_or_404(Question, pk=pk)

    def get(self, request, pk):
        return render(
            request,
            self.template_name,
            dict(question=self.get_object(pk)))

    def post(self, request, pk):
        question = self.get_object(pk)
        form = question.edit_form(request.POST)
        question = form.save(commit=False)
        question.save()
        return HttpResponseRedirect(reverse("likert-edit-question",
                                            args=[question.id]))
