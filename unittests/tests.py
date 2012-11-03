"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.test.client import Client
from surveys.models import Survey, Question, Choice, Surveyee, Answer
from django.utils import timezone
from django.contrib.auth.models import User

# Tests for the index() method
class IndexTest(TestCase):
    def setUp(self):
        self.c = Client()

    # Tests for Anonymous users
    # New surveys view test
    def test_new(self):
        # Create dummy user
        testUser = User.objects.create(username='user', password=make_password("password"), birthday="2013-01-19")

        # Model testing: Survey model
        # Create dummy PUBLISHED survey
        testSurvey = Survey.objects.create(title="Test survey", information="Test survey", status=Survey.STATUS_PUBLISHED, resultDisplay=Survey.RESULTS_PUBLIC, owner=testUser, created=timezone.now(), starttime=timezone.now(), endtime=timezone.timedelta(days=3)+timezone.now())

        #Model testing: Question model
        #Create dummy Question
        testQuestion = Question.objects.create(survey=testSurvey, question="question1",instruction="this is a test question")

        #Model testing: Choice model
        #Create dummy Choice
        testChoice = Choice.objects.create(question=testQuestion, choice="ChoiceA", votes="0")

        #Model testing: Surveyee model
        #Create dummy Surveyee
        testSurveyee = Surveyee.objects.create(survey=testSurvey, question=testQuestion, user=testUser, ip="119.56.116.109", starttime=timezone.now(), endtime="")

        #Model testing: Answer model
        #Create dummy Answer
        testAnswer = Answer.objects.create(question=testQuestion, value="My dummy answer")


        # Survey should be correctly created
        self.assertIsInstance(testSurvey, Survey)

        # Question should be correctly created
        self.assertIsInstance(testQuestion, Question)

        # Choice should be correctly created
        self.assertIsInstance(testChoice, Choice)

        # Surveyee should be correctly created
        self.assertIsInstance(testSurveyee, Surveyee)

        # Answer should be correct created
        self.assertIsInstance(testAnswer, Answer)




        # Tests for different views
        # /?view=1 corresponds to viewing "newest" surveys
        response = self.c.get('/?view=1')
        self.assertTrue("survey_list" in response.context)
        # Anonymous users should be able to see this section, so length of the list should be >= 1
        self.assertGreaterEqual(len(response.context["survey_list"]), 1)
        # Page displayed correctly for Anonymous users
        self.assertEqual(response.status_code, 200)

    def test_popular(self):
        response = self.c.get('/?view=2')
        self.assertTrue("survey_list" in response.context)

        self.assertEqual(response.status_code, 200)

    def test_all(self):
        response = self.c.get('/?view=3')
        self.assertTrue("survey_list" in response.context)

        self.assertEqual(response.status_code, 200)

    def test_recently_ended(self):
        response = self.c.get('/?view=4')
        self.assertTrue("survey_list" in response.context)

        self.assertEqual(response.status_code, 200)

    # Active surveys view test
    def test_active(self):

        # /?view=5 corresponds to viewing "active" surveys
        response = self.c.get('/?view=5')
        self.assertTrue("survey_list" in response.context)
        # Anonymous users should not be able to see this section, so length of the list should be 0
        self.assertEqual(len(response.context["survey_list"]), 0)
        # Page displayed correctly for Anonymous users (no 404 or 500 error code)
        self.assertEqual(response.status_code, 200)

    def test_deleted(self):
        response = self.c.get('/?view=6')
        self.assertTrue("survey_list" in response.context)
        self.assertEqual(len(response.context["survey_list"]), 0)

        self.assertEqual(response.status_code, 200)

        # TODO: Create tests for Users

        # TODO: Create tests for Admins