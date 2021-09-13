Feature:

    Scenario: create a user and test login function
        Given A user's username is user1
        And A user's password is abcdefg
        When Enter the /accounts/login/ page
        Then The user login success

    Scenario: login and visit 'repository' page
        Given username: user2, password: abcdefg
        When Visit the 'repository' page
        Then Show 'project' title