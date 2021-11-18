from core.utils import ENVIRON

from jenkins import Jenkins

"""新增一個共用的 Jenkins Instance"""
jenkins_url = f'http://{ENVIRON["JENKINS_HOST"]}:{ENVIRON["JENKINS_PORT"]}'
root = (ENVIRON['JENKINS_ROOT_USERNAME'], ENVIRON['JENKINS_ROOT_PASSWORD'])
jenkins_inst = Jenkins(jenkins_url, username=root[0], password=root[1])
del root
