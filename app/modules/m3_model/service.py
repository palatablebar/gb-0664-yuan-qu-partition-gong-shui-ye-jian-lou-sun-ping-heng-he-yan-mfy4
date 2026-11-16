import json
from app.config import SAMPLE_DIR
from app.modules.m2_contract.service import run as previous
from .rules import validate_catalog,validate_repair_orders,match,reversed_match,night,order_for
def run(options=None):
    result=previous(options)
    catalog=json.loads((SAMPLE_DIR/"catalog.json").read_text())
    orders=json.loads((SAMPLE_DIR/"repair_orders.json").read_text())
    result["zones"]=validate_catalog(catalog)
    orders=validate_repair_orders(orders,catalog)
    valid=[];reverse=[]
    for row in result["rows"]:
        if match(row,catalog):valid.append(row);continue
        if reversed_match(row,catalog):
            order=order_for(orders,row["meter"],row["at"])
            if order and night(row["at"]):
                row["flow"]="reverse"
                reverse.append({"line":row["line"],"meter":row["meter"],"from_zone":row["from_zone"],"to_zone":row["to_zone"],"value_m3":row["value_m3"],"at":row["at"],"order_date":order["date"],"order_note":order["note"]})
                valid.append(row)
            else:result["quarantine"].append({"line":row["line"],"code":"DIRECTION","raw":row.get("source",row)})
        else:result["quarantine"].append({"line":row["line"],"code":"REFERENCE","raw":row.get("source",row)})
    result["rows"]=valid
    result["reverse_flows"]=reverse
    result["repair_orders"]=orders
    result["catalog"]=catalog
    return result
