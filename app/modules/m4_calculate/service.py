from app.modules.m3_model.service import run as previous
from .rules import balances
def run(options=None):
    result=previous(options)
    result["results"]=balances(result["rows"],result["zones"])
    result["night_results"]=balances(result["rows"],result["zones"],True)
    return result
