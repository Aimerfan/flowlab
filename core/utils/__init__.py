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

# read {project_root}/ci/static/jenkins/multibranch_config.xml as python string
CONFIG_XML = ElementTree.parse('ci/static/jenkins/multibranch_config.xml').getroot()
CONFIG_XML = ElementTree.tostring(CONFIG_XML).decode()
CONFIG_XML = CONFIG_XML.replace('set_username', ENVIRON['GITLAB_ROOT_USERNAME'])
CONFIG_XML = CONFIG_XML.replace('set_password', ENVIRON['GITLAB_ROOT_PASSWORD'])
