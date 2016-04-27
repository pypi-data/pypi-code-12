from django import forms

class ScoredTextarea(forms.Textarea):
    class Media:
        js = ['js/content_scoring.js']

    def __init__(self, score, *args, **kwargs):
        kwargs.setdefault('attrs',{}).update({'class': 'score%d'%score})
        super(ScoredTextarea, self).__init__(*args, **kwargs)
