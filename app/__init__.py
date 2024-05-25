from pathlib import Path
import os


ROOT_PATH = Path(__file__).parent.parent

date_cache = ROOT_PATH / './date_cache'

if not os.path.exists(date_cache):
    with open(date_cache, 'w') as f:
        pass