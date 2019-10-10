import os
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import pygit2
import time
import tempdata
from pygit2 import clone_repository
from pygit2 import RemoteCallbacks
from pygit2.errors import GitError
from distutils.errors import DistutilsFileError


class Codecommitrepo:
    def __init__(self, repo_name: str, username: str, region: str, password: str, committer_email: str,
                 branch_name: str):
        self.client = boto3.client('codecommit')
        self.committer_email = committer_email
        self.username = username
        self.password = password
        self.repo_name = repo_name
        self.branch_name = branch_name
        self.region = region
        self.default_repo_folder = '/tmp/repositories'
        self.old_repo = '{}/old-{}'.format(self.default_repo_folder, self.repo_name.split('/')[1])
        self.new_repo = '{}/{}'.format(self.default_repo_folder, self.repo_name.split('/')[1])
        self.github_repos_url = 'https://git-codecommit.{}.amazonaws.com/v1/repos/{}'.format(self.region,
                                                                                             self.repo_name.split('/')[
                                                                                                 1])
        self.error = False
        self.tmp = tempdata.Tempdata(repo_name=self.repo_name)

    def get_commit_id(self) -> str:
        if self.error:
            pass
        else:
            try:
                response = self.client.get_branch(
                    repositoryName=self.repo_name.split('/')[1],
                    branchName='master'
                )
                return response.get('branch').get('commitId')
            except (ClientError, BotoCoreError)as error:
                print(error)
                self.error = True
                exit(code='All bad')

    def create_new_branch(self) -> bool:
        if self.error:
            return False
        else:
            try:
                self.client.create_branch(
                    repositoryName=self.repo_name.split('/')[1],
                    branchName=self.branch_name,
                    commitId=self.get_commit_id()
                )

                return True
            except (ClientError, BotoCoreError) as error:
                print(error)
                self.error = True
                return False

    def label_file_code_commit(self) -> bool:
        if self.error:
            return False
        else:
            try:
                if self.branch_name == 'master':
                    self.client.put_file(
                        repositoryName=self.repo_name.split('/')[1],
                        branchName=self.branch_name,
                        fileContent=b'version1',
                        filePath='{}-label-file'.format(time.strftime("%H-%M-%m-%d-%Y", time.localtime(time.time()))),
                        fileMode='NORMAL',
                        commitMessage='label',
                        name='script'
                    )
                    return True
                else:
                    self.create_new_branch()
            except (ClientError, BotoCoreError) as error:
                self.error = True
                return False

    def clone_from_codecommit(self) -> bool:
        if self.error:
            return False
        else:
            try:
                cred = pygit2.UserPass(username=self.username, password=self.password)
                callbacks = RemoteCallbacks(credentials=cred)
                clone_repository(
                    url=self.github_repos_url,
                    path=self.new_repo,
                    callbacks=callbacks, checkout_branch=self.branch_name)
                if os.path.exists(path='{}/.git'.format(self.new_repo)):
                    return True
                else:
                    return False
            except GitError as error:
                print(error)
                self.error = True
                return False

    def copy_data_to_new_repo(self) -> bool:
        if self.error:
            return False
        else:
            try:
                os.system('rm -Rf {}/*'.format(self.new_repo))
                #os.system('cp -r {} {}'.format(self.old_repo, self.new_repo))
                os.system('cp -rT {} {}'.format(self.old_repo, self.new_repo)) # Not working -T with MacOS
                return True
            except (GitError, FileNotFoundError, DistutilsFileError) as error:
                self.delete_wrong_branch()
                print(error)
                self.error = True
                return False

    def add_commit_repo(self) -> bool:
        if self.error:
            return False
        else:
            repo = pygit2.Repository(path=self.new_repo)
            status = repo.status()
            message = 'update'
            try:
                committer = pygit2.Signature('update', self.committer_email)
                for filepath, flags in status.items():
                    index = repo.index
                    index.read()
                    if os.path.exists('{}/{}'.format(self.new_repo, filepath)):
                        index.add(path_or_entry='{}'.format(filepath))
                        index.write()
                        tree = index.write_tree()
                        parents = repo.lookup_branch(self.branch_name).target
                        repo.create_commit('refs/heads/{}'.format(self.branch_name), committer, committer, message,
                                           tree,
                                           [parents])
                    else:
                        index.remove(path='{}'.format(filepath))
                        index.write()
                        tree = index.write_tree()
                        parents = repo.lookup_branch(self.branch_name).target
                        repo.create_commit('refs/heads/{}'.format(self.branch_name), committer, committer, message,
                                           tree,
                                           [parents])
                return True
            except (GitError, AttributeError) as error:
                print(error)
                self.error = True
                return False

    def push_code(self) -> bool:
        if self.error:
            self.tmp.delete_temp_data()
            return False
        else:
            try:
                local = pygit2.Repository(path=self.new_repo)
                cred = pygit2.UserPass(username=self.username, password=self.password)
                callbacks = RemoteCallbacks(credentials=cred)
                remote = local.remotes['origin']
                remote.push(callbacks=callbacks, specs=['refs/heads/{}'.format(self.branch_name)])
                return True
            except GitError:
                self.error = True
                return False

    def delete_wrong_branch(self):
        try:
            self.client.delete_branch(
                repositoryName=self.repo_name.split('/')[1],
                branchName=self.branch_name
            )
            print('Branch: {} creation error'.format(self.branch_name))

        except (ClientError, BotoCoreError) as error:
            print(error)
