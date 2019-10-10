import zipfile
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import os


class S3archive:
    def __init__(self, repo_name: str, branch: str):
        self.branch = branch
        self.repo_name = repo_name.split('/')[1]
        self.repo_path = '/tmp/repositories/{}'.format(self.repo_name)
        self.bucket_name = 'git-archive-bucket-{}'.format(self.repo_name)
        self.zip_file_name = '{}-{}.zip'.format(self.repo_name, self.branch)
        self.client = boto3.client('s3')

    def create_bucket(self) -> bool:
        try:

            buckets_list = self.client.list_buckets()
            for item in buckets_list.get('Buckets'):
                if item.get('Name') == self.bucket_name:
                    return True
            self.client.create_bucket(ACL='private', Bucket=self.bucket_name)
            return True
        except (ClientError, BotoCoreError):
            return False

    def zip_archive(self) -> bool:
        try:
            zipped = zipfile.ZipFile(file='{}/{}'.format(self.repo_path, self.zip_file_name), mode='w',
                                     compression=zipfile.ZIP_DEFLATED)
            for root, subfolder, files in os.walk(self.repo_path):
                for file_name in files:
                    if file_name != self.zip_file_name:
                        zipped.write(os.path.join(root, file_name))
            return True
        except Exception:
            return False

    def copy_data_s3(self) -> bool:
        try:
            s3 = boto3.resource('s3')
            s3.meta.client.upload_file('{}/{}'.format(self.repo_path, self.zip_file_name),
                                       '{}'.format(self.bucket_name), '{}'.format(self.zip_file_name))
            return True
        except (ClientError, BotoCoreError):
            return False
