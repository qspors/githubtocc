import requests
import json


class Branch:
    def __init__(self, repo_name: str, api_key: str):
        self.repo_name = repo_name
        self.api_key = api_key

    def get_branches_list(self) -> list:
        url_branch = "https://api.github.com/repos/{}/branches".format(self.repo_name)
        branch_list = ['master']
        headers = {
            'Authorization': "Bearer {}".format(self.api_key),
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "api.github.com",
            'Accept-Encoding': "gzip, deflate",
            'Cookie': "logged_in=no",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        try:
            response = json.loads(requests.request("GET", url=url_branch, headers=headers).text)
            for item in response:
                branch_list.append(item.get('name'))
            return branch_list
        except Exception as error:
            print(error)
