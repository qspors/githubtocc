import pygit2
from pygit2 import clone_repository
from pygit2 import RemoteCallbacks
import json
import requests
import os
import shutil
from requests.exceptions import HTTPError
from pygit2.errors import GitError


class Githubrepo:
    def __init__(self, repo_name: str, api_key: str, branch: str):
        self.branch = branch
        self.repo_name = repo_name
        self.default_repo_folder = '/tmp/repositories'
        self.old_repo = '{}/old-{}'.format(self.default_repo_folder, self.repo_name.split('/')[1])
        self.github_repos_url = 'https://api.github.com/repos/{}'.format(self.repo_name)
        self.api_key = api_key

    def archive_github_repo(self) -> bool:
        payload = json.dumps({"name": self.repo_name.split('/')[1], "archived": True})
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer {}".format(self.api_key),
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "api.github.com",
            'Accept-Encoding': "gzip, deflate",
            'Content-Length': "48",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        try:
            git_hub_response = json.loads(
                requests.request("PATCH", self.github_repos_url, data=payload, headers=headers).text).get('archived')
            if git_hub_response is None or git_hub_response is True:
                return True
            else:
                return False
        except HTTPError:
            return False

    def check_branch_is_exist(self) -> bool:
        pass

    def clone_from_github(self) -> bool:
        try:
            callbacks = RemoteCallbacks(pygit2.UserPass(self.api_key, 'x-oauth-basic'))
            clone_repository(url='https://github.com/{}'.format(self.repo_name),
                             path=self.old_repo,
                             callbacks=callbacks, checkout_branch=self.branch)
            if os.path.exists(path='{}/.git'.format(self.old_repo)):
                return True
            else:
                return False
        except (GitError, ValueError) as error:
            print(error)
            return False

    def remove_old_git_artifacts(self) -> bool:
        try:
            shutil.rmtree(path='{}/.git'.format(self.old_repo), ignore_errors=False)
            return True
        except IOError:
            return False
