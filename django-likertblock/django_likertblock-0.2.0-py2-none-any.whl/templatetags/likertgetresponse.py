from django import template
from likertblock.models import Response, Submission

register = template.Library()


class GetQuestionResponseNode(template.Node):
    def __init__(self, question, var_name):
        self.question = question
        self.var_name = var_name

    def render(self, context):
        q = context[self.question]
        u = context['request'].user
        questionnaire = q.questionnaire
        r = Submission.objects.filter(
            questionnaire=questionnaire, user=u).order_by("-submitted")
        if r.count() == 0:
            return ''
        submission = r[0]
        r = Response.objects.filter(question=q, submission=submission)
        if r.count() > 0:
            context[self.var_name] = r[0]
        else:
            context[self.var_name] = None
        return ''


@register.tag('getquestionresponse')
def getquestionresponse(parser, token):
    question = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetQuestionResponseNode(question, var_name)
