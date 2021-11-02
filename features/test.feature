Feature:

    Scenario: create a user and test login function
        Given A user's username is user1
        And A user's password is abcdefg
        When Enter the /accounts/login/ page
        Then The user login success

    Scenario: use exist user to login and visit 'repository' page
        Given username: usertest, password: passpass1
        When Visit the 'repository' page
        Then Show 'project' title