import datetime
from django.db import models
from django.forms import ModelForm

class Survey(models.Model):
    title = models.CharField(max_length=100)
    information = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Date published', auto_now_add=True)

    def __unicode__(self):
        return self.title

class Question(models.Model):
    survey = models.ForeignKey(Survey)
    question = models.CharField(max_length=200)
    instruction = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.question

class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField(editable=False, default=0)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.choice

    def percentage(self):
        totalVotes = sum(c.votes for c in self.question.choice_set.all())
        percent = 100.0 * float(self.votes) / float(totalVotes)
        return percent
