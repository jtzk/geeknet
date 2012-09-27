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
        (None,                  {'fields': ['title', 'information']}),
        ]
    inlines = [QuestionInline]

    list_display = ('title', 'information', 'pub_date')

class QuestionAdmin(admin.ModelAdmin):
    fields = ['survey', 'question', 'instruction']
    inlines = [ChoiceInline]

    list_display = ('survey', 'question', 'instruction')

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)