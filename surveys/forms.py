__author__ = 'Jarryd'

from django import forms
from surveys.models import Survey, Question

class SurveyCreationForm(forms.ModelForm):
    class Meta:
        model = Survey
        exclude = {'status', 'owner', 'resultDisplay', 'created', 'starttime', 'endtime'}

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        widgets = {
            'type': forms.RadioSelect(),
            }
        exclude = ('survey',)