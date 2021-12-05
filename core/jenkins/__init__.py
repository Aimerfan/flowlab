from jenkins import Jenkins
from xml.etree import ElementTree

from core.config import ENVIRON


"""新增一個共用的 Jenkins Instance"""
JENKINS_URL = f'http://{ENVIRON["JENKINS_HOST"]}:{ENVIRON["JENKINS_PORT"]}'
_root_secret = (ENVIRON['JENKINS_ROOT_USERNAME'], ENVIRON['JENKINS_ROOT_PASSWORD'])
JENKINS_ = Jenkins(JENKINS_URL, username=_root_secret[0], password=_root_secret[1])
del _root_secret


def load_multibranch_xml():
    """
    載入 {project_root}/ci/static/ci/multibranch_config.xml
    並轉換為 python String
    """
    xml = ElementTree.parse('ci/static/ci/multibranch_config.xml').getroot()
    xml = ElementTree.tostring(xml).decode()
    xml = xml.replace('set_username', ENVIRON['GITLAB_ROOT_USERNAME'])
    xml = xml.replace('set_password', ENVIRON['GITLAB_ROOT_PASSWORD'])
    return xml


# Jenkins Multibranch Jobs 預設模板設定
CONFIG_XML = load_multibranch_xml()
