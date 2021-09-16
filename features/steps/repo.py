from behave import given, when, then


@given('username: {username}, password: {password}')
def given_user_info(context, username, password):
    context.username = username
    context.test.client.post('/accounts/login/', {'username': username, 'password': password})
    response = context.test.client.get('')
    context.test.assertContains(response, 'Logout')


@when("Visit the 'repository' page")
def visit_repo_page(context):
    context.response = context.test.client.get(f'/repo/{context.username}/')
    context.test.assertEqual(context.response.status_code, 200)


@then("Show 'project' title")
def visit_success(context):
    context.test.assertContains(context.response, 'projects')
