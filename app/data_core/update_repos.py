'''
All logic related to updating the other git repos.
'''

import os
import git

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

REPO_URL = 'https://github.com/robinnarsinghranabhat/nepse-floorsheet-daily-scrape.git'  # Replace with the actual repo URL
LOCAL_REPO_PATH = '/Users/robinakan/projects/nepse-analytics-backend/dependency/floorsheet_repo'

def clone_or_pull_repo():
        
    if not os.path.exists(LOCAL_REPO_PATH):
        logging.info("Cloning Repo")
        os.makedirs(LOCAL_REPO_PATH)
        fs_repo = git.Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)
    else:
        logging.info("Repo Exists. Pulling latest changes.")
        fs_repo = git.Repo(LOCAL_REPO_PATH)
        origin = fs_repo.remotes.origin
        origin.pull()

# clone_or_pull_repo()