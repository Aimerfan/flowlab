from abc import ABCMeta, abstractmethod


class VCSAdapter(metaclass=ABCMeta):
    # _instance = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, url, token=None, user=None, repo=None):
        self.url = url
        self.token = token
        self.user = user
        self.repo = repo

    @staticmethod
    def timedelta_str(seconds: int):
        """
        將相差秒數轉換為描述字串
        """
        # 時間單位與使用該單位的秒數上限
        unit_dict = {
            'second': 60,
            'minute': 60 * 60,
            'hour': 60 * 60 * 24,
            'day': 60 * 60 * 24 * 7,
            'week': 60 * 60 * 24 * 7 * 4,
            'month': 60 * 60 * 24 * 30 * 12,
            'year': None
        }
        prev_max = 1
        for unit, max_sec in unit_dict.items():
            if unit == 'year' or seconds < max_sec:
                redundant = seconds // prev_max
                plural = 's' if redundant > 1 else ''
                return f'Updated {redundant} {unit}{plural} ago'
            else:
                prev_max = max_sec

    @abstractmethod
    def get_repo_list(self, user):
        """
        取得所有 repo 名稱, 最後 commit 日期(距離今天多久前), branch 總數
        :param user:
        :return: {
            'flowlab': {
                'last_activity_at': 'Updated 3 minutes ago',
            },
            ...
        }
        """
        pass

    @abstractmethod
    def get_repo(self, user, repo):
        """
        取得 repo 名稱, branch 總數,
        :param user:
        :param repo:
        :return: {
            'name': 'flowlab',
            'default_branch': 'master',
        }
        """
        pass

    @abstractmethod
    def get_branches(self, user, repo):
        """
        取得所有 branch 名稱
        :param user:
        :param repo:
        :return: {
            'master': {
                'default': True,
                'commit': {
                    'short_id': '78b3472',
                    'title': 'init commit',
                    'author_name': 'aimerfan',
                    'last_activity_at': 'Updated 3 minutes ago',
                }
            },
            'dev': {
                ...
            },
            ...
        }
        """
        pass

    @abstractmethod
    def get_commits(self, user, repo, branch):
        """
        取得該 branch 下(最新) commit 的 sha, 訊息, 作者名, 日期(距離今天多久前)
        :param user:
        :param repo:
        :param branch:
        :return: {
            '78b3472': {
            }, ...
        }
        """
        pass

    @abstractmethod
    def get_tree(self, user, repo, path=None, ref=None):
        """
        取得指定的 git 檔案結構樹(tree)
        :param user:
        :param repo:
        :param path: 指定要搜尋的樹的路徑
        :param ref: 指定分支(或tag...), 未指定表示預設分支
        :return: {}
        """
        pass

    @abstractmethod
    def get_blob(self, user, repo, blob_sha):
        """
        取得指定的 git 檔案結構樹(tree)
        :param user:
        :param repo:
        :param blob_sha: 指定要取得的檔案sha
        :return: {}
        """
        pass
