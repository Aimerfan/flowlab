from behave import given, when, then, step
from django.contrib.auth.models import User


@given("A user's username is {username:S}")
def login_user_name(context, username):
    context.username = username


@step("A user's password is {password:S}")
def login_user_password(context, password):
    context.password = password


@when("Enter the {url} page")
def enter_login_page(context, url):
    context.url = url
    response = context.test.client.get(url)
    context.test.assertContains(response, '登入 FlowLab')


@then('The user login success')
def test_login_success(context):
    User.objects.create_user(username=context.username, password=context.password)
    context.test.client.login(username=context.username, password=context.password)
    response = context.test.client.get(context.url)
    context.test.assertContains(response, 'Logout')
