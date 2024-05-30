"""
All logic related to updating the other git repos.
"""

import logging
import os

import git

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def clone_or_pull_repo(repo_url, local_repo_path):
    """
    Download Git Repositories
    """
    if not os.path.exists(local_repo_path):
        logging.info("Cloning Repo")
        os.makedirs(local_repo_path)
        fs_repo = git.Repo.clone_from(repo_url, local_repo_path)
    else:
        logging.info("Repo Exists. Pulling latest changes.")
        repo = git.Repo(local_repo_path)
        origin = repo.remotes.origin
        origin.pull()


# clone_or_pull_repo()
