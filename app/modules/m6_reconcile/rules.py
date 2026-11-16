from decimal import Decimal
from app.errors import reject
def classify(item,threshold):
    threshold=Decimal(str(threshold))
    if not threshold.is_finite() or threshold<0:reject("THRESHOLD","阈值须为非负数")
    if Decimal(item["lower"])>threshold:return "漏损"
    if Decimal(item["upper"])<0:return "倒挂"
    return "待观察" if Decimal(item["residual"])>threshold else "通过"
def reconcile(data,threshold="5"):
    rows=data["rows"];supply=sum((Decimal(x["value_m3"]) for x in rows if x["kind"]=="supply"),Decimal(0))
    sales=sum((Decimal(x["value_m3"]) for x in rows if x["kind"]=="sale"),Decimal(0))
    auth=sum((Decimal(x["value_m3"]) for x in rows if x["kind"]=="authorized"),Decimal(0))
    residual=sum((Decimal(x["residual"]) for x in data["results"]),Decimal(0))
    for item in data["results"]:item["status"]=classify(item,threshold)
    for item in data.get("night_results",[]):item["status"]=classify(item,threshold)
    count_ok=data["input_count"]==len(rows)+len(data["quarantine"])+data["blank_count"]
    return {"supply":str(supply),"sales":str(sales),"authorized":str(auth),"residual":str(residual),"balanced":supply==sales+auth+residual,"count_ok":count_ok,"accepted":len(rows),"quarantined":len(data["quarantine"])}
