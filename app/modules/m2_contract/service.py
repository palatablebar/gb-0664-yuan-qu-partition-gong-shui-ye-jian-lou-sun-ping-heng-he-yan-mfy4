from app.modules.m1_intake.service import run as previous
from app.errors import DomainError
from .rules import normalize,deduplicate
def run(options=None):
    result=previous(options);rows=[]
    for row in result["rows"]:
        try:rows.append(normalize(row))
        except DomainError as exc:result["quarantine"].append({"line":row["line"],"code":exc.code,"raw":row.get("source",row)})
    result["rows"],bad=deduplicate(rows);result["quarantine"]+=bad
    result["contract"]={"volume":"m3","timezone":"UTC","key":"record_id","boundary":"[start,end)"}
    return result
