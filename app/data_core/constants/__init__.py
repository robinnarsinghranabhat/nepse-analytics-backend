"""
Prepare Utility Contants
- Company Details
"""

import glob
import json
import os
import time

import pandas as pd
from nepse import Nepse

SECTORS = [
    "Finance",
    "Hydro Power",
    "Microfinance",
    "Commercial Banks",
    "Development Banks",
]

## Generic Company List
with open("app/data_core/constants/company_list.json") as json_file:
    company_list = json.load(json_file)
company_dict = {}
for i in company_list:
    key = i["symbol"]
    company_dict[key] = i


## Details on Each Company
save_dir = "app/data_core/constants/company_details"
CACHE_COMPANY_DETAILS = True

nepse = Nepse()
nepse.headers["Connection"] = "close"
nepse.setTLSVerification(
    False
)  # This is temporary, until nepse sorts its ssl certificate problem


def get_company_details(symbols):
    os.makedirs(save_dir, exist_ok=True)
    for symbol in symbols:
        save_path = os.path.join(save_dir, f"{symbol}.json")
        if CACHE_COMPANY_DETAILS and os.path.exists(save_path):
            continue
        time.sleep(1)
        try:
            data = nepse.getCompanyDetails(symbol)
        except Exception as e:
            print(f"ERROR << {str(e)} >>  : {symbol}")
            continue
        if not data:
            print(f"NO DATA FOR  : {symbol} ")
            continue

        try:
            with open(save_path, "w") as json_file:
                json.dump(data, json_file)
        except FileNotFoundError:
            print("SYMBOL IGNORED : ", symbol)

    company_details_paths = glob.glob(f"./{save_dir}/*.json")
    all_details = []
    for path in company_details_paths:
        try:
            with open(path) as f:
                data = json.load(f)
            all_details.append(data)
        except Exception as e:
            print(f"ERROR {e} :: while loading : ", path)

    all_details = pd.DataFrame(all_details)

    all_details["instrument"] = all_details["security"].apply(
        lambda x: x["instrumentType"]["description"]
    )

    all_details["company_name"] = all_details["security"].apply(
        lambda x: x["companyId"]["companyName"]
    )
    all_details["symbol"] = all_details["security"].apply(lambda x: x["symbol"])

    return all_details
