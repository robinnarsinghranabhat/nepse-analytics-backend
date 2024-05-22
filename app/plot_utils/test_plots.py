
# %%
for sector, df in all_dfs.groupby('sector'):
    print(sector)
    df_des = df[['Symbol', 'stockListedShares']].drop_duplicates(subset=['Symbol']).sort_values(by='stockListedShares').head(10)
    print(df_des)

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


