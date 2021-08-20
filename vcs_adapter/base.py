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
        pass

    @abstractmethod
    def get_repo(self, user, repo):
        pass

    @abstractmethod
    def get_branches(self, user, repo):
        pass

    @abstractmethod
    def get_commits(self, user, repo, branch):
        pass

    @abstractmethod
    def get_tree(self, user, repo, path=None, ref=None):
        """
        取得指定的 git 檔案結構樹(tree)
        :param user:
        :param repo:
        :param path: 指定要搜尋的樹的路徑
        :param ref: 指定分支(或tag...), 未指定表示預設分支
        """
        pass

    @abstractmethod
    def get_blob(self, user, repo, blob_sha):
        """
        取得指定的 git 檔案結構樹(tree)
        :param user:
        :param repo:
        :param blob_sha: 指定要取得的檔案sha
        """
        pass
