from datetime import datetime, timedelta

def generate_date_list(start_date_str, end_date_str, exclude_days=['Friday', 'Saturday']):
    # Convert start and end date strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Initialize an empty list to store dates
    date_list = []

    # Iterate through dates from start to end, adding each date to the list
    current_date = start_date
    while current_date <= end_date:
        if current_date.strftime('%A') not in exclude_days:
            date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_list


REPO_URL = 'https://github.com/robinnarsinghranabhat/nepse-floorsheet-daily-scrape.git'  # Replace with the actual repo URL
LOCAL_REPO_PATH = '/Users/robinakan/projects/nepse-analytics-backend/dependency/floorsheet_repo'

def clone_or_pull_repo():
    if not os.path.exists(LOCAL_REPO_PATH):
        logging.info("Cloning Repo")
        os.makedirs(LOCAL_REPO_PATH)
        fs_repo = git.Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)
    else:
        logging.info("Repo Exists. Pulling latest changes.")
        repo = git.Repo(LOCAL_REPO_PATH)
        origin = repo.remotes.origin
        origin.pull()


clone_or_pull_repo()