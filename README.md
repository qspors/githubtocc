# GithubtoCC v.1.0
Fast and easy migrate repository with hundreds branches from Github to AWS CodeCommit.

This python script automatically migrate repository with all branches (master by default must be exist first in order) from github.com to AWS CodeCommit.
After migration this script make extra copy of repository with all branches to AWS S3 Bucket.
Migrated repository in github turn to archive state.
Before start you must make preparations.
Create "SSM" parameters,Username and Password for AWS CodeCommit, "IAM" permissions (IAMPolicy.json - Minimum permissions)
and generate "Gihub" API-KEY for repo witch will be migrated.

## Parameters:
```
-v Github account name.
-r Repository name.
-e Committer Email address.
-b Branches ( use comma for separate branches except master, master must be first in order, if you want to migrate all branches just put "-b all").
-rg AWS Region Name, for AWS CodeCommit.
                
```
## Configuration:
1.) Need to create AWS Secret manager values
   AWS CodeCommit Username and Password must be in AWS secret manager:
 ```
    path = /prd/repo/codecommit
    Key=username, Value=AWS CodeCommit username, Key=password, Value=AWS CodeCommit password
 ```
   GitHub API must be associated with repo which will be migrated.
```   
    path = /prd/repo/gitapi, Key=api, Value=GitHub API
```
2.) AWS Access Key, AWS Secret Key and Region name must be specified thru "aws configure" command
    Go to AWS IAM , generate new access and secret key with appropriate Policy for Secret manager, CodeCommit and S3 bucket.
    Associate new Policy with Role and User.
 
3.) You can invoke handler.py from remote machine or on EC2 instance. Please check requirements.txt for install python libs.
   
```
     mkdir foldername
     virtualenv foldername -p python3
     source foldername/bin/activate
     cd foldername
     pip install -r requirements.txt
     git clone repository_link
     python3 app/handler.py -v accountname -r reponame -e example@gmail.com -b master,dev,1.2,v5 -rg us-east-1
 ```
 Yuriy Yurov
 
 qspors@gmail.com