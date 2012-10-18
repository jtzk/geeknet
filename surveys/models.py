import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    # status types
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_PUBLISHED = 2
    STATUS_ENDED = 3

    STATUS_CHOICES = (
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ENDED, 'Ended'),
        )

    # results types
    RESULTS_PUBLIC = 0
    RESULTS_USER = 1
    RESULTS_PRIVATE = 2

    RESULTS_CHOICES = (
        (RESULTS_PUBLIC, 'Public (Anyone can see)'),
        (RESULTS_USER, 'Users (Users can see)'),
        (RESULTS_PRIVATE, 'Hidden (Only you can see)')
    )

    title = models.CharField(max_length=100)
    information = models.CharField(max_length=200)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    resultDisplay = models.IntegerField(choices=RESULTS_CHOICES, default=RESULTS_PUBLIC)
    owner = models.ForeignKey(User)
    created = models.DateTimeField()
    starttime = models.DateTimeField('Start time', null=True, default=None)
    endtime = models.DateTimeField('End time', null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(Survey, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def results(self):
        results = {"timesAttempted":0, "numberQuestions":0, "totalVotes":0,}

        results["numberQuestions"] = self.question_set.all().count
        #results["totalVotes"] += self.question_set.all().aggregate(tvotes=Sum('choice__votes'))['tvotes']
        results["participants"] = self.surveyee_set.all().count

        return results

    @property
    def numQuestions(self):
        return self.question_set.count()

    @property
    def participants(self):
        return self.surveyee_set.all().count()

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
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    ip = models.GenericIPAddressField(blank=True)
    starttime = models.DateTimeField('Start Time', default=datetime.datetime.now())
    endtime = models.DateTimeField('End Time', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.starttime = datetime.datetime.now()
            self.endtime = None
        super(Surveyee, self).save(*args, **kwargs)

    def end(self):
        self.endtime = datetime.datetime.now()
        super(Surveyee, self).save()

class Answer(models.Model):
    question = models.ForeignKey(Question)
    value = models.TextField(blank=True)

    def __unicode__(self):
        return self.value