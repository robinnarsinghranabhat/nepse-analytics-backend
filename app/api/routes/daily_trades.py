from typing import Any, List, Optional, Annotated

from fastapi import APIRouter, Body, Query

from pydantic import BaseModel

from app.core.config import settings
from app.data_core.update_repos import clone_or_pull_repo
from app.data_core.trade_history import prices_db

router = APIRouter()


DEFAULT_SECTORS = ["Finance"]  ## Load this from DB or true Datasourcce !
DEFAULT_TOP_N = 3


@router.post("/get-historical-data")
def dummy_response(
    sectors: list[str] = DEFAULT_SECTORS, top_n: int = DEFAULT_TOP_N
) -> Any:
    """
    Endpoint to receive a list of strings and a number,
    and return a dummy response.
    """
    # Dummy response
    response = {"message": "Received input data", "strings": sectors, "number": top_n}
    return response


@router.get("/update-daily-prices")
async def update_daily_prices():
    try:
        clone_or_pull_repo(
            settings.DAILY_PRICES_REPO_URL, settings.DAILY_PRICES_LOCAL_REPO_PATH
        )
        return {
            "status": "success",
            "err": "No Error",
        }
    except Exception as e:
        return {"status": "failure", "err": str(e)}


@router.get("/update-floorsheets")
async def update_floorsheets():
    try:
        clone_or_pull_repo(settings.FS_REPO_URL, settings.FS_LOCAL_REPO_PATH)
        return {
            "status": "success",
            "err": "No Error",
        }
    except Exception as e:
        return {"status": "failure", "err": str(e)}


## -- STOCK DATA API -- ##

START_DATE = "2023-01-01"
END_DATE = "2024-01-01"


class DateRange(BaseModel):
    start: Optional[str] = START_DATE
    end: Optional[str] = END_DATE


class StockFilter(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    sortOrder: Optional[str] = "asc"


@router.post("/stocks")
async def get_stocks(
    stockNames: Annotated[list[str], Query()] = None,
    sectors: Optional[List[str]] = Query(default=[]),
    topN: Optional[int] = Query(default=10),
    stock_date_range: DateRange = Body(),
    promoter_shares: StockFilter = Body(
        default=StockFilter(min=0, max=100, sortOrder="ignore")
    ),
    listed_shares: StockFilter = Body(
        default=StockFilter(min=0, max=100000000, sortOrder="asc")
    ),
):
    # Simulate fetching data based on the filters
    if stockNames:
        data = prices_db[
            (prices_db.Symbol.isin(stockNames))
        ]    
    if sectors:
        data = prices_db[
            (prices_db.sector.isin(sectors))
        ]

    data = data[
        (data.date_scraped >= stock_date_range.start)
        & (data.date_scraped <= stock_date_range.end)
    ]
    # Apply Promoter Share filter
    data = data[
        (data.promoterPercentage >= promoter_shares.min) &
        (data.promoterPercentage <= promoter_shares.max) 
    ]

    # Apply StockListedShare filter
    data = data[
        (data.stockListedShares >= listed_shares.min) &
        (data.stockListedShares <= listed_shares.max) 
    ]

    if listed_shares.sortOrder == 'asc':
        temp = data.groupby('Symbol').apply( lambda x : x.head(1))
        temp = temp.sort_values(by=['stockListedShares'], ascending=True)
        lowest_listed_shares = temp['Symbol'][:topN].tolist()
        data = data[ data.Symbol.isin(lowest_listed_shares) ] 
    

    output_response = [] ## 'symbol_name' : {x : [], y : []}
    for symbol, df in data.groupby('Symbol'):
        df = df.sort_values('date_scraped', ascending=True)
        item = {
            'symbol' : symbol 
        }

        item.update(
            df[['date_scraped', 'Close']].to_dict('list')
        )
        
        output_response.append(item)


    return output_response
