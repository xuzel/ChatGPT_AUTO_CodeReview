from django.shortcuts import render
from django.http import HttpResponse
from pydriller import Repository
import typing


def url_preprocess(url: str) -> typing.Dict[str, str]:
    """
    输入url比如：https://github.com/anc95/ChatGPT-CodeReview/commit/26625e44efdc890b97f6c5452e442c366cac95d5
    解析出仓库地址https://github.com/anc95/ChatGPT-CodeReview/
    解析出哈希值26625e44efdc890b97f6c5452e442c366cac95d5
    :param url: commit的url
    :return:一个字典，包含解析内容
    {
        'url': 'https://github.com/anc95/ChatGPT-CodeReview/',
        'hash': '26625e44efdc890b97f6c5452e442c366cac95d5'
    }
    """
    # TODO
    return {
        'url': '',
        'hash': ''
    }


def get_commit_diff(repositories_address: str, commit_hash: str) -> typing.Dict[str, typing.List]:
    """
    输入仓库地址以及哈希值，获取这个commit中全部的文件变更存储在字典中返回
    :param repositories_address:仓库地址
    :param commit_hash:commit哈希值
    :return:一个字典，字典的key是变更的文件名，value是一个列表，包含了文件全部变更信息
    """
    # TODO
    return {
        'file_name1': ["file change 1", "file change 2", "..."],
        'file_name2': ["file change 1", "file change 2", "..."],
        'file_name3': ["file change 1", "file change 2", "..."]
    }


def example():
    from pydriller import Repository
    for commit in Repository('https://github.com/xuzel/ChatGPT_AUTO_CodeReview').traverse_commits():
        if commit.hash != 'e846355798e3fca1bbf94fa173cd731b11b5753e':
            continue
        # print(commit.hash)
        # print(commit.msg)
        # print(commit.author.name)

        for file in commit.modified_files:
            print(file.diff)
            break
        break


def main_code_diff_compare(request):
    return render(request, 'main_ui.html')
