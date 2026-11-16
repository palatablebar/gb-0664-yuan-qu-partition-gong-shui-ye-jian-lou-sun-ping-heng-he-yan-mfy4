from decimal import Decimal
from app.modules.m3_model.rules import night
def balances(rows,zones,night_only=False):
    results=[]
    for zone in zones:
        values={x:Decimal(0) for x in ("inflow","outflow","sale","authorized","uncertainty")};lines=[]
        for row in rows:
            if night_only and not night(row["at"]):continue
            value=Decimal(row["value_m3"])
            if zone==row["to_zone"]:values["inflow"]+=value
            elif zone==row["from_zone"]:
                values[{"transfer":"outflow","sale":"sale","authorized":"authorized"}.get(row["kind"],"outflow")]+=value
            else:continue
            values["uncertainty"]+=abs(value)*Decimal(row["error_pct"])/100;lines.append(row["line"])
        residual=values["inflow"]-values["outflow"]-values["sale"]-values["authorized"]
        results.append({"zone":zone,**{k:str(v) for k,v in values.items()},"residual":str(residual),"lower":str(residual-values["uncertainty"]),"upper":str(residual+values["uncertainty"]),"lines":lines})
    return results
