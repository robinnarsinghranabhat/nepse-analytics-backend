""" 
- Loads in-memory Dataframe to handle API requests for
    - Custom Analytics Dashboard
- Final Goal of Dashboad :
    - For low-volume, top traiding stocks
"""


import glob
import logging
from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd

from app import date_cache
from app.core.config import settings
from app.data_core.constants import company_dict, get_company_details
from app.data_core.data_utils import _str_to_int, generate_date_list


def load_daily_trades(data_path):
    """
    `data_path` : Directory with csv files for daily prices.

    NOTE : As Time progresses, this will be memory intensive.
    """
    all_dfs = []
    for fpath in glob.glob(data_path + "/*.csv"):
        date = fpath.split("/")[-1].strip(".csv")
        per_day_df = pd.read_csv(fpath)
        per_day_df["date_scraped"] = date
        all_dfs.append(per_day_df)

    all_dfs = pd.concat(all_dfs)
    all_dfs["date_scraped"] = pd.to_datetime(all_dfs["date_scraped"], format="%m_%d_%Y")
    all_dfs["day_of_week"] = all_dfs["date_scraped"].dt.day_name()

    # Merge Company Details
    all_dfs = all_dfs[~all_dfs["day_of_week"].isin(["Friday", "Saturday"])]
    all_dfs.shape

    all_dfs.drop_duplicates(
        subset=["Symbol", "date_scraped", "Open", "High", "Low", "Close", "Vol"],
        inplace=True,
    )

    all_dfs["sector"] = all_dfs.Symbol.apply(
        lambda x: company_dict.get(x, {}).get("sectorName", "NA")
    )

    return all_dfs


# all_dfs = load_daily_trades()
def filter_scrips(all_dfs: pd.DataFrame):
    """
     Remove Irrelavant Scripts
    - Scrips which have less trading dates
    - Filter rows by Initial Secondary market listing Date of Stocks
    - Remove symbols with less than 1 month of Trading histroy
    """

    # Ensure the symbols are present in last 30 days
    PAST_N_DAYS = 30

    start_day = str(date.today() - timedelta(PAST_N_DAYS))
    end_day = str(date.today())

    approx_nepse_days = generate_date_list(start_day, end_day)

    latest = all_dfs[all_dfs["date_scraped"] >= start_day]

    all_dfs = all_dfs[all_dfs.Symbol.isin(latest.Symbol.unique())]

    latest["diff"] = None

    differences = []
    for _, df in latest.groupby("Symbol"):
        diff = len(approx_nepse_days) - len(df)
        differences.append(diff)
        df["diff"] = diff

    med_diff = np.median(differences)
    print(f"Median Trading Days in past {PAST_N_DAYS} days : {med_diff}")

    irrelavant_stocks = []
    for _, df in latest.groupby("Symbol"):
        if _ == "EBLCP":
            print("stopping")
            break
        diff = len(approx_nepse_days) - len(df)
        if diff > (med_diff + 5):
            irrelavant_stocks.append(_)

    print("Filtered out Following Stocks : ", irrelavant_stocks)
    all_dfs = all_dfs[~all_dfs.Symbol.isin(irrelavant_stocks)]
    return all_dfs


def merge_company_details_and_filter(all_dfs: pd.DataFrame):
    """
    # Filter companies like : Promotor share, debentures, mutual funds e.t.cc

    """
    all_details = get_company_details(all_dfs.Symbol.unique())
    all_dfs = all_dfs.merge(
        all_details[
            [
                "company_name",
                "symbol",
                "instrument",
                "stockListedShares",
                "publicShares",
                "publicPercentage",
                "promoterShares",
                "promoterPercentage",
            ]
        ],
        left_on=["Symbol"],
        right_on=["symbol"],
        how="left",
    )

    symbol_filter_keywords = ["promoter share", "debenture"]
    all_dfs = all_dfs[
        ~all_dfs["company_name"]
        .astype(str)
        .str.contains("|".join(symbol_filter_keywords), case=False)
    ]
    all_dfs = all_dfs[all_dfs.instrument == "Equity"]
    return all_dfs


def final_data_cleanup(all_dfs: pd.DataFrame):
    """
    - Type Cast numeric columns
    - Listed Shares less than 100 is absurd

    """
    num_cols = ["Open", "High", "Low", "Close", "Vol"]
    for num_col in num_cols:
        all_dfs[num_col] = all_dfs[num_col].apply(lambda x: _str_to_int(x))

    for col in num_cols:
        all_dfs = all_dfs[all_dfs[col] != -1]

    all_dfs["Vol"] = all_dfs["Vol"] / 1000

    # Remove more irrelevant
    bad_symbols = all_dfs[all_dfs["stockListedShares"] < 100].Symbol.unique()
    print("These stocks have listed shares < 100. Can you believe it ? ", bad_symbols)
    all_dfs = all_dfs[~all_dfs.Symbol.isin(bad_symbols)]

    df_memory_usage = all_dfs.memory_usage(deep=True).sum()
    print(" Consumed Memory of all_dfs in MB : ", df_memory_usage / 1024 / 1024)

    return all_dfs


def load_historical_db(data_path):

    today = str(datetime.today().date())
    with open(date_cache, "r+") as f:
        cached_date = f.read()
        if cached_date == today:
            logging.info("Loading Cached Historical-Trade DB")
            return pd.read_csv("./cached_db.csv")
        else:
            f.seek(0)
            f.write(today)
            f.truncate()
    
    logging.info("Initiazing Historical-Trade DB load")
    all_dfs = load_daily_trades(data_path)
    all_dfs = filter_scrips(all_dfs)
    all_dfs = merge_company_details_and_filter(all_dfs)
    all_dfs = final_data_cleanup(all_dfs)
    logging.info("Completed Historical-Trade DB load")

    all_dfs.to_csv("./cached_db.csv", index=False)
    return all_dfs

prices_db = load_historical_db(settings.daily_trades_csv_path)
