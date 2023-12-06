from django.shortcuts import render
from django.http import HttpResponse
from pydriller import Repository
from urllib.parse import urlparse
import typing
import code_compare.code_reviewer.code_review as code_review

codereview = code_review.CoseReview()


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
    # 复制URL
    parsed_url = urlparse(url)

    # 分离URL与harsh
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
            file_diff = file.diff.splitlines()
            file_changes[file_name] = file_diff
            break
        break

    return file_changes


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


code_diff = """
            '--name', build_environment_container_name,
            '-v', f'{host_working_dir}:{container_working_directory}',
            '-v', f'{host_install_scripts_dir}:{container_install_scripts_dir}',
+           packaging_config.builder_dockerhub_image
-           packaging_config.builder_image
        ]
        subprocess.run(build_environment_startup_cmd, check=True)

"""


def main_code_diff_compare(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        return render(request, 'main_ui.html')
    elif request.method == 'GET':
        print('get')
        return render(request, 'main_ui.html')
