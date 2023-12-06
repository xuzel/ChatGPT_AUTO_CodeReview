import re

from django.shortcuts import render
from django.http import HttpResponse
from pydriller import Repository
from urllib.parse import urlparse
import typing
import code_compare.code_reviewer.code_review as code_review

codereview = code_review.CoseReview()
data_dict = dict()
file_name_list = list()
change_dict = dict()


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
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')
    repository_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{'/'.join(path_segments[:-2])}"
    commit_hash = path_segments[-1]
    return {
        'url': repository_url,
        'hash': commit_hash
    }


def get_commit_diff(repositories_address: str, commit_hash: str) -> typing.Dict[str, typing.List]:
    """
    输入仓库地址以及哈希值，获取这个commit中全部的文件变更存储在字典中返回
    :param repositories_address:仓库地址
    :param commit_hash:commit哈希值
    :return:一个字典，字典的key是变更的文件名，value是一个列表，包含了文件全部变更信息
    """
    file_changes = dict()

    for commit in Repository(repositories_address).traverse_commits():
        if commit.hash != commit_hash:
            continue
        for file in commit.modified_files:
            file_name = file.filename
            file_diff = file.diff
            file_changes[file_name] = list()
            sections = re.split(r'@@.*?@@', file_diff)
            for i, section in enumerate(sections):
                if not i:
                    continue
                file_changes[file_name].append(section)
    return file_changes


def main_code_diff_compare(request):
    global data_dict
    global file_name_list
    global change_dict
    if request.method == 'POST':
        data_dict = dict()
        file_name_list = list()
        change_dict = dict()
        search = request.POST.get('search')
        url, commit_hash = url_preprocess(search)['url'], url_preprocess(search)['hash']
        change_dict = get_commit_diff(url, commit_hash)
        # print(change_dict)
        for file_name, changes in change_dict.items():
            file_name_list.append(file_name)
            data_dict[file_name] = list()

            for each_change in changes:
                one_pice_change = list()
                change_in_line = each_change.splitlines()
                for each_line in change_in_line:
                    if not each_line or each_line == ' ':
                        continue
                    if each_line.startswith('+'):
                        one_pice_change.append([each_line, 0])
                    elif each_line.startswith('-'):
                        one_pice_change.append([each_line, 1])
                    else:
                        one_pice_change.append([each_line, 2])
                data_dict[file_name].append(one_pice_change)
        print(data_dict)

        return render(request, 'main_ui.html', {'file_name': file_name_list})
    elif request.method == 'GET':
        file_name = request.GET.get('file')
        print(file_name)
        if data_dict.get(file_name):
            print(data_dict[file_name])
            change_code_and_command = list()
            for index, value in enumerate(change_dict[file_name]):
                change_code_and_command.append({
                    'data': data_dict[file_name][index],
                    'command': codereview.generate(change_dict[file_name][index])
                })

            return render(request, 'main_ui.html', {'file_name': file_name_list, 'change_dict': change_code_and_command})
        return render(request, 'main_ui.html', {'file_name': file_name_list})