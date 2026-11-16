from app.modules.m4_calculate.service import run as previous
from app.modules.m5_quarantine.service import summarize
from .rules import reconcile
def run(options=None):
    result=previous(options)
    result["reconciliation"]=reconcile(result,(options or {}).get("params",{}).get("threshold","5"))
    summarize(result)
    return result
