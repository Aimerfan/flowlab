# 靜態字典檔


# 建立新的模板專案時的模板來源
REPO_TEMPLATES_SRC = {
    'local': {
        'templates': [
            # ('檔案名稱', '可讀名稱')
            ('gradle.tar.gz', 'Gradle'),
        ],
    },
    'gitlab': {
        'base_url': 'https://gitlab.com/',
        'templates': [
            # ('namespace/repo_name', '可讀名稱')
            ('flowlab2/gradle', 'Gradle'),
        ],
    }
}
