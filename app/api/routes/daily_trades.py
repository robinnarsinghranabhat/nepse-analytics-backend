from typing import Any
import pandas as pd

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.data_core.update_repos import clone_or_pull_repo


router = APIRouter()


DEFAULT_SECTORS = ["Finance"] ## Load this from DB or true Datasourcce ! 
DEFAULT_TOP_N = 3

@router.post("/get-historical-data")
def dummy_response(
    sectors: list[str] = DEFAULT_SECTORS, 
    top_n: int= DEFAULT_TOP_N) -> Any:
    """
    Endpoint to receive a list of strings and a number,
    and return a dummy response.
    """
    # Dummy response
    response = {
        "message": "Received input data",
        "strings": sectors,
        "number": top_n
    }
    return response


@router.get("/update-floorsheets")
async def update_floorsheets():
    try:
        clone_or_pull_repo()
        return {
            "status" : "success",
            "err" : "No Error",
        }
    except Exception as e:
        return {"status" : "failure", "err" : str(e)}