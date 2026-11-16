import unicodedata
from decimal import Decimal,InvalidOperation
from datetime import datetime,timezone
from app.config import SENTINELS
from app.errors import reject
FACTORS={"m3":Decimal(1),"L":Decimal("0.001")}
def number(value):
    text=unicodedata.normalize("NFKC",str(value)).strip().replace(",","")
    if text in SENTINELS:reject("MISSING","必要值缺失")
    try:v=Decimal(text)
    except InvalidOperation:reject("VALUE","数值无效")
    if not v.is_finite():reject("VALUE","数值非有限")
    return v
def normalize(row):
    from app.errors import DomainError
    value=number(row["value"]);pct=number(row["error_pct"])
    if value<0:reject("NEGATIVE","负向计量")
    if not Decimal(0)<=pct<=Decimal(10):reject("UNCERTAINTY","误差超限")
    unit=row["unit"].strip()
    if unit not in FACTORS:reject("UNIT","单位未知")
    try:
        at=datetime.fromisoformat(row["at"].replace("Z","+00:00"))
        if at.tzinfo is None:raise ValueError()
    except ValueError:reject("TIME","时间无效")
    for key in ("record_id","meter","from_zone","to_zone","kind"):
        if row[key].strip() in SENTINELS:reject("MISSING","必要值缺失")
    return {**row,"source":{k:v for k,v in row.items() if k!="line"},"value_m3":str(value*FACTORS[unit]),"error_pct":str(pct),"at":at.astimezone(timezone.utc).isoformat()}
def deduplicate(rows):
    groups={};good=[];bad=[]
    for row in rows:groups.setdefault(row["record_id"],[]).append(row)
    for key,items in groups.items():
        keys={tuple((k,str(v)) for k,v in sorted(row.items()) if k!="line") for row in items}
        if len(keys)>1:bad.extend({"line":x["line"],"code":"CONFLICT","raw":x} for x in items)
        else:
            good.append(items[0]);bad.extend({"line":x["line"],"code":"DUPLICATE","raw":x} for x in items[1:])
    return good,bad
