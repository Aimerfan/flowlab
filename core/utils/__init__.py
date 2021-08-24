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
