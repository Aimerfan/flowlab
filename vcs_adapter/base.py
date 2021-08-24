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

    @abstractmethod
    def get_repo_list(self, user):
        """
        取得所有 repo 名稱, 最後 commit 日期(距離今天多久前), branch 總數
        :param user:
        :return: {
            'flowlab': {
                'name': 'flowlab',
                'last_time': '3 minutes ago',
                'branch_sum': 4,
            },
        }
        """
        pass

    @abstractmethod
    def get_repo(self, user, repo):
        """
        取得 repo 名稱, branch 總數,
        目前 branch 名稱, 最後 commit sha, 訊息與日期(距離今天多久前)
        :param user:
        :param repo:
        :return: {
            'name': 'flowlab',
            'branch_sum': 4,
            'branch': 'master',
            'sha': '78b3472',
            'author_name': 'aimerfan',
            'last_info': 'init commit',
            'last_time': '3 minutes ago',
        }
        """
        pass

    @abstractmethod
    def get_branches(self, user, repo):
        """
        取得所有 branch 名稱
        :param user:
        :param repo:
        :return: ['master', 'dev']
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
                'sha': '78b3472',
                'info': 'init commit',
                'author_name': 'aimerfan',
                'last_time': '3 minutes ago',
            },
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
