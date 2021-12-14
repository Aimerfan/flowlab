# functools


def get_job_name(user, project, branch=''):
    # multibranch pipline 專案實際上比較像 "每個分支一個 job 的 folder"
    # 因此如果給定 branch name, job_name 要把原本 job_name 當成 folder, 再加上分支名稱
    if branch:
        return f'{user}_{project}/{branch}'
    else:
        return f'{user}_{project}'
