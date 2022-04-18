from django.test import TestCase, client
from django.contrib.auth.models import User
from django.db import transaction


class IndexTestCase(TestCase):

    def setUp(self):
        self.c = client.Client()

    def test_index_page(self):
        response = self.c.get('')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>FlowLab</h1>')
        self.assertTemplateUsed(response, 'index.html')
        return response


class LoginTestCase(TestCase):

    def setUp(self):
        self.sid = transaction.savepoint()
        self.c = client.Client()
        User.objects.create_user(username='user', password='abcde')

    def login(self):
        login = self.c.login(username='user', password='abcde')
        self.assertEqual(login, True)
        return login

    def check_login_success(self):
        self.login()
        response = self.c.get('')
        self.assertEqual(response.status_code, 200)
        result = self.assertContains(response, 'Logout')
        transaction.savepoint_rollback(self.sid)
        return result
