import shutil


class Tempdata:
    def __init__(self, repo_name: str):
        self.repo_name = repo_name.split('/')[1]
        self.default_repo_folder = '/tmp/repositories'
        self.old_repo = '{}/old-{}'.format(self.default_repo_folder, self.repo_name)
        self.new_repo = '{}/{}'.format(self.default_repo_folder, self.repo_name)

    def delete_temp_data(self) -> bool:
        try:
            shutil.rmtree(path='{}'.format(self.old_repo), ignore_errors=False)
            shutil.rmtree(path='{}'.format(self.new_repo), ignore_errors=False)
            return True
        except IOError:
            return False
