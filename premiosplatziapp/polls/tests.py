import datetime
from urllib import response


from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse

from .models import Question

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """
        was_publisehed_recently returns false for question whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="¿Quien es el mejor Course Director de platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_whith_past_questions(self):
        """was_published_recently return False for question whose pub_date is in the past"""
        time = timezone.now() - datetime.timedelta(days=30)
        past_question = Question( question_text="¿Quien es el mejor Course Director de Platzi?", pub_date = time )
        self.assertIs(past_question.was_published_recently(), False)
    
    def test_was_published_recently_whith_present_questions(self):
        """
        was_published_recently return False for question whose pub_date is in the present
        """
        time = timezone.now()
        present_question = Question( question_text="¿Quien es el mejor Course Director de Platzi?", pub_date = time )
        self.assertIs(present_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    create a question with the given "question_text", and published the given
    number of days offset to now (negative for questions published in the past,
    positive for questions that have yet to be publisehed)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date= time)
    
class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
    
    def test_questions_with_future_pub_date(self):
        """
            Questions with a pub_date greater than the current date should not appear in the Index View.
        """
        create_question("future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_questions(self):
        """
        questions with a pub_date in the past are displayed on the index page
        """
        question = create_question("past question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past question are dispalyed
        """
        past_question = create_question(question_text="past question", days=-30)
        future_question = create_question(question_text="past question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question]
        )

    def test_two_past_question(self):
        """
        The questions index page may display multiple questions
        """
        past_question1 = create_question(question_text="past question1", days=-30)
        past_question2 = create_question(question_text="past question2", days=-40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1, past_question2]
        )

    def two_future_questions(self):
        """
        the quesions index page may display multiple questions
        """
        future_question1 = create_question("future question",days=30)
        future_question2 = create_question("future question",days=50)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The ditail view of a question with a pub_date in teh future 
        returns a 404 error nat found
        """
        future_question = create_question(question_text="future question", days=30)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the questions text
        """
        past_question = create_question(question_text="past question", days=-30)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionResultViewTests(TestCase):
    def test_no_question(self):
        """
        The result view of a question that doesn't exist
        return a 404 error not found
        """
        url = reverse("polls:results", args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question(self):
        """
        The result view of a question with a pub_date in the future
        return a 404 error not found
        """
        future_question = create_question(question_text="¿Quien es el mejor Course Director de Platzi?", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The result view of a question with a pub_date in the past
        displays the question's text
        """
        past_question = create_question(question_text="Past question", days=-30)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionModelTests(TestCase):

    def test_create_question_without_choices(self):
        """If the questions hasn't choices it is deleted."""

        question = Question.objects.create(
            question_text="¿Quien es el mejor CD de Platzi?",
            pub_date=timezone.now(),
            choices=0)

        if question.choices <= 1:
            question.delete()

        questions_count = len(Question.objects.all())

        self.assertEqual(questions_count, 0)