# webapp/pomo/get_version.py

import subprocess
import datetime

def get_git_commit_hash():
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
        return commit_hash
    except subprocess.CalledProcessError:
        return 'unknown'

def write_version_file():
    commit_hash = get_git_commit_hash()
    with open('static/pomo/version.txt', 'w') as f:
        f.write(commit_hash)

def get_version():
    now = datetime.datetime.now()
    version = now.strftime('%Y%m%d-%H%M')
    return version

def write_version2_file():
    version = get_version()
    with open('static/pomo/version.txt', 'w') as f:
        f.write(version)

if __name__ == '__main__':
    write_version2_file()