import boto3
import json
import requests
import os
from requests.exceptions import InvalidSchema
from botocore.exceptions import BotoCoreError, ClientError


class Checklist:
    def __init__(self, repo_name: str, api_key: str):
        self.repo_name = repo_name
        self.short_repo_name = self.repo_name.split('/')[1]
        self.api_key = api_key
        self.default_repo_folder = '/tmp/repositories'
        self.old_repo = '{}/old-{}'.format(self.default_repo_folder, self.short_repo_name)
        self.new_repo = '{}/{}'.format(self.default_repo_folder, self.short_repo_name)
        self.github_repos_url = 'https://api.github.com/repos/'
        self.client = boto3.client('codecommit')

    def local_repo_folder_existing(self) -> bool:
        try:
            if os.path.exists(self.default_repo_folder):
                pass
            else:
                os.mkdir(self.default_repo_folder)
                self.local_repo_folder_existing()
            return True
        except Exception as error:
            print(error)
            return False

    def codecommit_repo_existing(self) -> bool:
        existing_repo_list = []
        try:
            repo_response = self.client.list_repositories(
                sortBy='repositoryName',
                order='ascending'
            )
            for item in repo_response.get('repositories'):
                existing_repo_list.append(item.get('repositoryName'))

            if self.short_repo_name in existing_repo_list:
                
                return True
            else:
                return self.create_codecommit_repos()
        except ClientError as error:
            print(error)
            return False
        except BotoCoreError as error:
            print(error)
            return False

    def github_repo_existing(self) -> bool:
        url = "{}{}".format(self.github_repos_url, self.repo_name)
        payload = ""
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer {}".format(self.api_key),
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "api.github.com",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        try:
            github_response = json.loads(requests.request("GET", url, data=payload, headers=headers).text)
            if github_response.get('message') == 'Not Found':
                return False
            elif github_response.get('name') == self.short_repo_name:
                return True
            else:
                return False
        except InvalidSchema as error:
            print(error)
            return False

    def create_codecommit_repos(self) -> bool:
        try:
            self.client.create_repository(
                repositoryName=self.short_repo_name,
                repositoryDescription='Migrated from GitHub',

            )
            return True
        except (ClientError, BotoCoreError) as error:
            print(error)
            return False
