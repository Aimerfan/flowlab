from xml.etree import ElementTree


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
