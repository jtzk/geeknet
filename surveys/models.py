from collections import defaultdict
import datetime
from django.db import models
from django.db.models import Sum

class Survey(models.Model):
    title = models.CharField(max_length=100)
    information = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Date published', auto_now_add=True)

    def __unicode__(self):
        return self.title

    def results(self):
        results = {"timesAttempted":0, "numberQuestions":0, "totalVotes":0,}

        results["numberQuestions"] = self.question_set.all().count
        results["totalVotes"] += self.question_set.all().aggregate(tvotes=Sum('choice__votes'))['tvotes']

        return results

class Question(models.Model):
    # question types
    TYPE_RADIO = 1
    TYPE_CHECKBOX = 2
    TYPE_TEXTBOX = 3
    TYPE_TEXTAREA = 4

    TYPE_CHOICES = (
        (TYPE_RADIO, 'Radio'),
        (TYPE_CHECKBOX, 'Checkbox'),
        (TYPE_TEXTBOX, 'Text Box'),
        (TYPE_TEXTAREA, 'Text Area'),
    )

    survey = models.ForeignKey(Survey)
    question = models.CharField(max_length=200)
    instruction = models.CharField(max_length=200, blank=True)
    type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_RADIO)
    number = 1

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.question

    def _get_prev(self):
        prev = self.survey.question_set.order_by('-id').filter(pk__lt=self.id)[0:1]
        if prev:
            return prev[0]
        return 0

    def _get_next(self):
        next = self.survey.question_set.order_by('id').filter(pk__gt=self.id)[0:1]
        if next:
            return next[0]
        return 0

    prev = property(_get_prev)
    next = property(_get_next)

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

        if totalVotes > 0:
            percent = 100 * self.votes / totalVotes
        else:
            percent = 0
        return percent

class Surveyee(models.Model):
    survey = models.ForeignKey(Survey)
    userid = models.IntegerField(default=0)





