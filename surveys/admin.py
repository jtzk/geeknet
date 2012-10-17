from surveys.models import Survey, Question, Choice
from django.contrib import admin

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class SurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['title', 'information', 'owner', 'resultDisplay', 'status', 'endtime']}),
        ]
    inlines = [QuestionInline]

    list_display = ('title', 'information', 'owner', 'starttime')

class QuestionAdmin(admin.ModelAdmin):
    fields = ['survey', 'question', 'instruction', 'type']
    inlines = [ChoiceInline]

    list_display = ('survey', 'question', 'instruction', 'type')

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)