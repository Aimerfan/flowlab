from requests.auth import HTTPBasicAuth
from gitlab import Gitlab
from jenkins import Jenkins
from sonarqube import SonarQubeClient


# read {project_root}/.env file as python objs.
ENVIRON = dict()
with open('.env', 'r', encoding='utf-8') as envfile:
    content = envfile.readlines()
    for line in content:
        line = line.strip()
        if line.startswith('#'):
            continue

        tokens = [token.strip() for token in line.split('=')]
        if len(tokens) == 2:
            ENVIRON[tokens[0]] = tokens[1]


"""共用的 GitLab Instance"""
GITLAB_URL = f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}'
GITLAB_ = Gitlab(GITLAB_URL, ENVIRON.get('GITLAB_ROOT_PRIVATE_TOKEN'))


"""新增一個共用的 Jenkins Instance"""
JENKINS_URL = f'http://{ENVIRON["JENKINS_HOST"]}:{ENVIRON["JENKINS_PORT"]}'
JENKINS_ = Jenkins(
    JENKINS_URL,
    username=ENVIRON['JENKINS_ROOT_USERNAME'],
    password=ENVIRON['JENKINS_API_TOKEN'],
)
JENKINS_AUTH = HTTPBasicAuth(
    ENVIRON['JENKINS_ROOT_USERNAME'],
    ENVIRON['JENKINS_API_TOKEN'],
)


"""新增一個共用的 SonarQube Instance"""
SONARQUBE_URL = f'http://{ENVIRON["SONARQUBE_HOST"]}:{ENVIRON["SONARQUBE_PORT"]}'
SONAR_ = SonarQubeClient(
    sonarqube_url=SONARQUBE_URL,
    username=ENVIRON["SONARQUBE_ROOT_USERNAME"],
    password=ENVIRON["SONARQUBE_ROOT_PASSWORD"]
)
