
## Load all csv
import pandas as pd
import glob

# ### IDEAS 
# - Custom Analytics Dashboard
#     - For low-volume, top traiding stocks ! 

all_dfs = []
for fpath in glob.glob('./data/*.csv'):
    date = fpath.split('/')[-1].strip('.csv')
    per_day_df = pd.read_csv(fpath)
    per_day_df['date_scraped'] = date
    all_dfs.append(per_day_df)

all_dfs = pd.concat(all_dfs)
all_dfs['date_scraped'] = pd.to_datetime(all_dfs['date_scraped'], format='%m_%d_%Y')
all_dfs['day_of_week'] = all_dfs['date_scraped'].dt.day_name()

# Merge Company Details
all_dfs = all_dfs[ ~all_dfs['day_of_week'].isin(['Friday','Saturday']) ]
all_dfs.shape

all_dfs.drop_duplicates(subset=['Symbol','date_scraped','Open', 'High', 'Low', 'Close', 'Vol'], inplace=True)

all_dfs.shape

### Remove Irrelavant Scripts ### 
# - Scrips which have less trading dates 
# - Filter rows by Initial Secondary market listing Date of Stocks
# - Remove symbols with less than 1 month of Trading histroy ! DONE ! 

from datetime import date, timedelta
from data_utils import generate_date_list
import numpy as np

# In the scrip variance
PAST_N_DAYS = 30

start_day = str( date.today() - timedelta(PAST_N_DAYS) )
end_day = str( date.today() )

approx_nepse_days = generate_date_list( start_day, end_day )

# Make sure the symbols are present in last 30 days ! 
latest = all_dfs[
    all_dfs['date_scraped']  >=  start_day
]

all_dfs = all_dfs[ all_dfs.Symbol.isin(latest.Symbol.unique()) ]

latest['diff'] = None

differences = []
for _, df in latest.groupby('Symbol'):
    diff = len(approx_nepse_days) - len(df) 
    differences.append( diff )
    df['diff'] = diff

med_diff = np.median(differences)
print(f"Median Trading Days in past {PAST_N_DAYS} days : {med_diff}")


irrelavant_stocks = []
for _, df in latest.groupby('Symbol'):
    if _ == 'EBLCP':
        print('stopping')
        break
    diff = len(approx_nepse_days) - len(df) 
    if diff > (med_diff + 5):
        irrelavant_stocks.append(_)

print("Filtered out Following Stocks : ", irrelavant_stocks)
all_dfs = all_dfs[ ~all_dfs.Symbol.isin(irrelavant_stocks) ]

# Merge Sector Column

import json
with open("company_list.json", "r") as json_file:
    company_list = json.load(json_file)
company_dict = {}
for i in company_list:
    key = i['symbol']
    company_dict[key] = i
del company_list
company_dict['MLBS']

all_dfs['sector'] = all_dfs.Symbol.apply( lambda x : company_dict.get(x, {}).get('sectorName', 'NA'))

### Filter by Sector
SECTORS = ['Finance', 'Hydro Power', 'Microfinance', 'Commercial Banks', 'Development Banks']
# all_dfs = all_dfs[ all_dfs.sector.isin( 
#     SECTORS
#  ) ]

# Merge Company Details 

from nepse import Nepse
import time
import os
import json


save_dir = './company_details'
CACHE_COMPANY_DETAILS = True

nepse = Nepse()
nepse.headers['Connection'] = 'close'
nepse.setTLSVerification(False) # This is temporary, until nepse sorts its ssl certificate problem


os.makedirs(save_dir, exist_ok=True)
for symbol in all_dfs.Symbol.unique():
    save_path = os.path.join( save_dir, f'{symbol}.json' )
    if CACHE_COMPANY_DETAILS and os.path.exists(save_path):
        continue
    time.sleep( 1 )
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
            json.dump( data, json_file )
    except FileNotFoundError:
        print("SYMBOL IGNORED : ", symbol)

company_details_paths = glob.glob( f'./{save_dir}/*.json' )
all_details = []
for path in company_details_paths:
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        all_details.append(data)
    except Exception as e:
        print(f"ERROR {e} :: while loading : ", path)

# %%
all_details = pd.DataFrame( all_details )

# %%
## Get different kind of instruments
all_details['instrument'] = all_details['security'].apply( lambda x : x['instrumentType']['description'] ) 
all_details['instrument'].value_counts()

# %%
all_details['company_name'] = all_details['security'].apply( lambda x : x['companyId']['companyName'])
all_details['symbol'] = all_details['security'].apply( lambda x : x['symbol'] )
all_dfs = all_dfs.merge( 
    all_details[
    ['company_name','symbol', 'instrument', 'stockListedShares', 'publicShares', 'publicPercentage', 'promoterShares','promoterPercentage']
    ], left_on=['Symbol'], right_on=['symbol'], how='left' )

print(all_details.columns)

# %% [markdown]
# ### Filtering companies
# - Promotor share, debentures, mutual funds e.t.cc 

# %%
all_dfs['company_name'].astype(str)

# %%
symbol_filter_keywords = ['promoter share', 'debenture']
all_dfs = all_dfs[ ~all_dfs['company_name'].astype(str).str.contains('|'.join(symbol_filter_keywords), case=False)]

# Only Take
all_dfs = all_dfs[all_dfs.instrument == 'Equity']

# %% [markdown]
# #### Change DTypes

# %%
from utils.plot_utils import plot_script, plot_candelstick
from utils.data_utils import longest_consecutive_dates, _str_to_int

num_cols = ['Open', 'High', 'Low','Close', 'Vol'] 
for num_col in num_cols:
    all_dfs[num_col] = all_dfs[num_col].apply(lambda x : _str_to_int(x))

for col in num_cols:
    all_dfs = all_dfs[ all_dfs[col] != -1 ]

all_dfs['Vol'] = all_dfs['Vol'] / 1000

# %% [markdown]
# ## Analyze the Stocks

# %%
all_dfs['stockListedShares']

# %%
## Remove more bad Data
bad_symbols = all_dfs[ all_dfs['stockListedShares'] < 100 ].Symbol.unique()
print(bad_symbols)
all_dfs = all_dfs[ ~all_dfs.Symbol.isin(bad_symbols) ]

# %%
all_details.iloc[0]['security']

# %%
df_memory_usage = all_dfs.memory_usage(deep=True).sum()
print(' Consumed Memory of all_dfs in MB : ', df_memory_usage / 1024 / 1024 )

# %% [markdown]
# ### Sectorwise listedshares distribution

# %%
for sector, df in all_dfs.groupby('sector'):
    print(sector)
    df_des = df[['Symbol', 'stockListedShares']].drop_duplicates(subset=['Symbol']).sort_values(by='stockListedShares').head(10)
    print(df_des)

# %% [markdown]
# ### Current Ongoing Analysis
# - SAMAJ stock volume droppage plot
# 
# A function that tells me : 
# - What stocks grew down a given day ? 
# - TAkes in df, date-column 
# - Let's test a couple of hypothesis ! Go Statistics !

# %%
all_dfs[ (all_dfs.Symbol == 'SAMAJ') & (all_dfs.date_scraped >= '2024-02-22') ].head(2)

# %% [markdown]
# ### Hypothesis to test
# - What happens to stocks after the lockin period ?
# - Does a sector go down when a particular stock goes down ?
# - Correlation between one sector booming and other sector increasing ?
# 
# ### Notes
# - Unless Right Shares, Volumnes are constant.
# - How to take into account right-shares and adjustment. 
# 

# %%
all_dfs.columns

# %% [markdown]
# ### Analyze a Script

# %%
def process_single_script(spec):

    spec.sort_values(by='date_scraped', inplace=True)
    # spec.reset_index(inplace=True)
    ## NOTE THIS SHOULD IDEALLY BE EMPTY. Othewise, check the DATA ! 
    # spec[spec.duplicated('date_scraped')]


    # spec['Vol_k'] = spec['Vol'].apply( lambda x : _str_to_int(x))

    # Filter out holidays ! 
    spec = spec[ ~spec['day_of_week'].isin(['Friday','Saturday']) ]

    _ = spec[ spec.duplicated( subset=['Open', 'High', 'Low', 'Close', 'Vol'] )]
    spec.drop_duplicates(subset=['Open', 'High', 'Low', 'Close', 'Vol'], inplace=True)
    return spec

# start_date, end_date = longest_consecutive_dates( spec['date_scraped'] )
# print('START : ', start_date, 'END : ', end_date)
# spec = spec[  (spec.date_scraped >= start_date) & (spec.date_scraped <= end_date) ]

def get_top_volumes(df):
    """
    Top N Traded Scripts. 
    """
    sector_stats = df.groupby('Symbol').agg({'Vol': 'sum', 'Open': 'sum',})

    sector_stats = sector_stats.sort_values('Vol', ascending=False)

    top_volumes = sector_stats.index.to_list()

    print(df.Symbol.unique())
    return top_volumes



import plotly.graph_objects as go

def plot_sector(top_sector_scrips):
    # Create a figure with subplots
    fig = go.Figure()

    # Add each subplot for each dataframe
    for symbol,df in top_sector_scrips.groupby('Symbol'):
        df = process_single_script(df)
        fig.add_trace(go.Scatter(x=df['date_scraped'], y=df['Open'], mode='lines', name=symbol))
        

    # Update axes settings
    fig.update_xaxes(type='category')
    # fig.update_yaxes(autorange="reversed")

    # Set layout options
    fig.update_layout(title='Stocks of Hydropower Sector', 
                    xaxis_title='Date', 
                    yaxis_title='Open Price')

    # Show the plot
    fig.show()





START_DATE = '2021-09-01'
TOP_VOL_COUNT = 5
SECTORS_TO_ANALYZE = SECTORS

# SECTORS_TO_ANALYZE = ['Hydro Power', 'Microfinance', 'Commercial Banks', 'Development Banks', 'Non Life Insurance', 'Development Banks','Manufacturing And Processing', ]
# for SECTOR in SECTORS_TO_ANALYZE:
#     # SECTOR = 'Hydro Power'

#     sector_df = all_dfs[ (all_dfs.sector == SECTOR) & ( all_dfs.date_scraped >= START_DATE) ]
#     top_volumes = get_top_volumes( sector_df ) 

#     top_sector_scrips = sector_df[ sector_df.Symbol.isin(top_volumes[:5]) ]
#     # top_sector_scrips.Symbol.unique()

#     plot_sector( top_sector_scrips )

df = all_dfs[ (all_dfs.sector == 'Microfinance') ]

all_dfs.sector.unique()

df.head(1)

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def grouped_stock_plot(grouped_df, sectors, TOP_N=10):
    """
    Plots Multiple stocks together at Sector-Level
    """
    # Define the number of rows and columns
    num_rows = len(sectors)
    num_cols = 1

    # Create a figure with subplots
    fig = make_subplots(rows=num_rows, cols=num_cols, subplot_titles=sectors)

    # Add each subplot for each dataframe
    for i, sector_name in enumerate(sectors, start=1):
        df = grouped_df[ (grouped_df.sector == sector_name) ]

        ### FILTER BY TOP VOLUMES WITHIN A GIVEN DATE-RANGE
        # top_volumes = get_top_volumes( df )[:TOP_VOL_COUNT]
        ### SYMBOLS WITH LEAST MARKET VOLUMES ! 
        least_shares = df.groupby('Symbol').agg( 
            {'Symbol' : 'first', 'stockListedShares': 'first'}
            ).sort_values('stockListedShares')
        least_shares = least_shares['Symbol'][:TOP_N].tolist()

        df = df[ df.Symbol.isin(least_shares  )]
        
        for symbol, df_grouped in df.groupby('Symbol'):
            df_processed = process_single_script(df_grouped)
            fig.add_trace(go.Scatter(x=df_processed['date_scraped'], y=df_processed['Close'], mode='lines', name=symbol), row=i, col=1)

    # Update axes settings
    fig.update_xaxes(type='category', row='all', col=1)
    fig.update_yaxes(autorange="reversed", row='all', col=1)

    # Set layout options
    fig.update_layout(title='Stocks of Hydropower Sector', 
                    xaxis_title='Date', 
                    yaxis_title='Closing Price',
                    height=1400,  # adjust height as needed
                    showlegend=True,
                    legend_traceorder='normal')

    # Show the plot
    fig.show()


SECTORS_TO_ANALYZE.append('Life Insurance')

grouped_stock_plot( all_dfs[ all_dfs.date_scraped >= '2024-01-01' ], SECTORS_TO_ANALYZE )
## All these stocks have :
# 1. Lowest Listed shares
# 2. 



## Sectorwise Top Scrip
sector_name = 'Microfinance'

df = all_dfs[ (all_dfs.sector == sector_name) & ( all_dfs.date_scraped >= START_DATE) ]

df.Symbol.unique()

spec = process_single_script( df[ df.Symbol == 'MLBS' ] )

plot_candelstick( spec )



# Get Company Details
from nepse_official import Nepse
nepse = Nepse()
nepse.setTLSVerification(False) #This is temporary, until nepse sorts its ssl certificate problem

spec_details = nepse.getCompanyDetails( spec.Symbol.iloc[0] )


