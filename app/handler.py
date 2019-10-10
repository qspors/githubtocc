import checklist as check_list
import credentials as credentials
import githubrepo as github
import codecommitrepo as codecommit
import s3archive as s3
import tempdata as temp_data
import branches as branches
import argparse

# region ARGS
env_data = argparse.ArgumentParser(description='Github migration Tool')
env_data.add_argument('-v', required=True, type=str, help='Specify GitHub account name')
env_data.add_argument('-r', required=True, type=str, help='Repository name')
env_data.add_argument('-e', required=True, type=str, help='Specify committer email')
env_data.add_argument('-b', required=True, type=str, help='Specify branches name')
env_data.add_argument('-rg', required=True, type=str, help='Specify AWS Region name')
# endregion

# region VARS
args = vars(env_data.parse_args())
ENV = args['v']
REPO = args['r']
EMAIL = args['e']
BRANCH = args['b']
REG = args['rg']
repo_name = '{}/{}'.format(ENV, REPO)
git_api = credentials.Credentials(cred_type='gitapi', region=REG).get_secret().get('api')
username_cc = credentials.Credentials(cred_type='codecommit', region=REG).get_secret().get('username')
password_cc = credentials.Credentials(cred_type='codecommit', region=REG).get_secret().get('password')
check = check_list.Checklist(repo_name=repo_name, api_key=git_api)
parsed_branch = []
bran = branches.Branch(repo_name=repo_name, api_key=git_api)
# endregion

for item in BRANCH.split(','):
    parsed_branch.append(item)
    if parsed_branch[0] == 'all':
        parsed_branch = bran.get_branches_list()
        parsed_branch = list(dict.fromkeys(parsed_branch))

print('Branch list is: {}'.format(parsed_branch))


def check_vars():
    passer = False
    if 'master' in parsed_branch:
        pass
    else:
        exit('Parameter branch is incorrect')
    if parsed_branch[0] == 'master':
        print('First branch is: {} : >'.format(parsed_branch[0]))
        passer = True
    else:
        exit('Parameter branch is incorrect')
    if REPO is not None:
        print('Repos is: {} : >'.format(REPO))
        passer = True
    else:
        exit('Parameter repo is incorrect')
    if passer is True:
        print('VARS test passed: >')
        execute_migration()
    else:
        exit('Parameters is incorrect')


def execute_migration():
    tmp = temp_data.Tempdata(repo_name=repo_name)

    for branch_item in parsed_branch:
        print('1) START JOB for branch')
        print('{}'.format(branch_item))
        git = github.Githubrepo(repo_name=repo_name, api_key=git_api, branch=branch_item)
        cc = codecommit.Codecommitrepo(repo_name=repo_name, username=username_cc, region=REG, password=password_cc,
                                       committer_email=EMAIL,
                                       branch_name=branch_item)
        archive = s3.S3archive(repo_name=repo_name, branch=branch_item)
        check.local_repo_folder_existing()
        print('2) Check CodeCommit')
        if check.codecommit_repo_existing():
            print('is exist')
            pass
        else:
            print('is not exist')
            break
        print('3) Archive github repo:')
        print('\"{}\" is: {}'.format(repo_name, git.archive_github_repo()))
        print('4) Clone github repo:')
        if git.clone_from_github():
            print('\"{}\", branch: \"{}\" Success'.format(repo_name.split('/')[1], branch_item))
        else:
            print('\"{}\", branch: \"{}\" Failed'.format(repo_name.split('/')[1], branch_item))
            tmp.delete_temp_data()
            continue
        print('5) Remove old .git folder:')
        print('{}'.format(git.remove_old_git_artifacts()))
        print('6) Create label for branch')
        if cc.label_file_code_commit() is False:
            print('{} is False'.format(branch_item))
            continue
        print('{} is Success'.format(branch_item))
        print('7) Clone repo')
        if cc.clone_from_codecommit() is False:
            print('\"{}\" , branch \"{}\" is Failed'.format(repo_name.split('/')[1], branch_item))
            continue
        print('Clone repo: \"{}\" , branch \"{}\" is Success'.format(repo_name.split('/')[1], branch_item))
        print('8) Copy data to new repo')
        print('\"{}\"'.format(cc.copy_data_to_new_repo()))
        print('9) Commit branch')
        print('\"{}\" is {}'.format(branch_item, cc.add_commit_repo()))
        print('10) Push data to CC for branch')
        if cc.push_code() is False:
            print('\"{}\" is Failed'.format(branch_item))
            continue
        print('\"{}\" is Success'.format(branch_item))
        archive.create_bucket()
        print('11) Archive old git branch')
        print('\"{}\" is: {}'.format(branch_item, archive.zip_archive()))
        print('12) Copy archive branch')
        print('\"{}\" to s3 bucket: {}'.format(branch_item, archive.copy_data_s3()))
        print('13) Delete data from temp folder')
        print('{}'.format(tmp.delete_temp_data()))
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('Completed for branch: \"{}\" !!!!!!!!!!!'.format(branch_item))
        print('######################### GO TO NEXT BRANCH  #############################')
    print('################################END###########################################')


if __name__ == "__main__":
    check_vars()
