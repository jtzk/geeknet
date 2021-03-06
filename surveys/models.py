import datetime
from django.template.defaultfilters import slugify
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Survey(models.Model):
    # status types
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_PUBLISHED = 2
    STATUS_ENDED = 3

    STATUS_CHOICES = (
        (STATUS_INACTIVE, 'Deleted'),
        (STATUS_ACTIVE, 'Unpublished'),
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
        results = {}

        results["numberQuestions"] = self.question_set.all().count
        #results["totalVotes"] += self.question_set.all().aggregate(tvotes=Sum('choice__votes'))['tvotes']
        results["participants"] = self.participants

        # get longest time taken to complete survey
        if self.participants > 0:
            totalDuration = shortestDuration = longestDuration = datetime.timedelta()
            for surveyee in self.surveyee_set.all().exclude(endtime=None):
                duration = surveyee.endtime - surveyee.starttime

                totalDuration += duration

                if duration < shortestDuration:
                    shortestDuration = duration
                elif shortestDuration.seconds == 0:
                    shortestDuration = duration

                if duration > longestDuration:
                    longestDuration = duration

            results["longest"] = timedelta_to_time(longestDuration)
            results["shortest"] = timedelta_to_time(shortestDuration)
            results["average"] = timedelta_to_time(totalDuration/self.surveyee_set.all().count())
        return results

    def publish(self, resultDisplay=RESULTS_PUBLIC, endtime=datetime.date.today()+datetime.timedelta(days=3)):
        if not self.status == self.STATUS_PUBLISHED:
            if any(int(resultDisplay) == r[0] for r in self.RESULTS_CHOICES):
                self.resultDisplay = int(resultDisplay)
            else:
                self.resultDisplay = self.RESULTS_PUBLIC
            if self.starttime == None:
                self.starttime = datetime.datetime.now()
            if endtime.date() <= datetime.date.today():
                self.endtime = datetime.date.today()+datetime.timedelta(days=3)
            else:
                self.endtime = endtime
            self.status = self.STATUS_PUBLISHED
            self.save()
            return True
        return False

    @property
    def numQuestions(self):
        return self.question_set.count()

    @property
    def participants(self):
        return self.surveyee_set.all().count()

    @property
    def slug(self):
        return slugify(self.title)

    def end(self):
        try:
            self.endtime = datetime.datetime.now()
            super(Survey, self).save()

            self.surveyee_set.all().filter(endtime=None).delete()

        except:
            return False
        return True

def timedelta_to_time(d):
    if d.seconds < 60:
        return "%d second(s)" % d.seconds
    if d.seconds < 3600:
        return "%d minute(s)" % (d.seconds/60)
    if d.seconds < 86400:
        return "%d hour(s)" % (d.seconds/3600)

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