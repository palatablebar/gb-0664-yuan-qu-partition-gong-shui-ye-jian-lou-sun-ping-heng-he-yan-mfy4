from datetime import date,datetime,timedelta,timezone
from app.errors import reject
CST=timezone(timedelta(hours=8))
def night(at):
    local=datetime.fromisoformat(at).astimezone(CST)
    return 0<=local.hour<5
def local_day(at):
    return datetime.fromisoformat(at).astimezone(CST).date().isoformat()
def cycle_path(edges):
    graph={}
    for a,b in edges:
        if a in {"EXT","OUT"} or b in {"EXT","OUT"}:continue
        graph.setdefault(a,[]).append(b)
    done=set();active=[]
    def visit(node):
        if node in active:return active[active.index(node):]+[node]
        if node in done:return []
        active.append(node)
        for nxt in sorted(graph.get(node,[])):
            found=visit(nxt)
            if found:return found
        active.pop();done.add(node);return []
    for node in sorted(graph):
        found=visit(node)
        if found:return found
    return []
def validate_catalog(catalog):
    edges=[]
    for meter,link in catalog.items():
        if len(link)!=3:reject("CATALOG","计量目录格式无效")
        a,b,kind=link
        if a==b:reject("CYCLE","计量目录有自环")
        if kind not in {"supply","transfer","sale","authorized"}:reject("CATALOG","计量类型无效")
        edges.append((a,b))
    path=cycle_path(edges)
    if path:reject("CYCLE","计量目录存在环："+"→".join(path))
    return sorted({x for edge in edges for x in edge}-{ "EXT","OUT"})
def match(row,catalog):
    return catalog.get(row["meter"])==[row["from_zone"],row["to_zone"],row["kind"]]
def reversed_match(row,catalog):
    link=catalog.get(row["meter"])
    if not link:return False
    a,b,kind=link
    return kind=="transfer" and row["kind"]==kind and row["from_zone"]==b and row["to_zone"]==a
def order_for(orders,meter,at):
    day=local_day(at)
    for order in orders:
        if order["meter"]==meter and order["date"]==day:return order
    return None
def validate_repair_orders(orders,catalog):
    if not isinstance(orders,list):reject("REPAIR_ORDER","抢修工单格式无效")
    seen=set();valid=[]
    for order in orders:
        if not isinstance(order,dict) or not {"meter","date"}<=set(order.keys()) or set(order.keys())-{"meter","date","note"}:reject("REPAIR_ORDER","抢修工单格式无效")
        meter=order["meter"];link=catalog.get(meter)
        if not link or link[2]!="transfer":reject("REPAIR_ORDER","工单计量表非转供边")
        try:day=date.fromisoformat(str(order["date"])).isoformat()
        except ValueError:reject("REPAIR_ORDER","工单日期无效")
        if (meter,day) in seen:reject("REPAIR_ORDER","抢修工单重复")
        seen.add((meter,day))
        valid.append({"meter":meter,"date":day,"note":str(order.get("note") or "")})
    return valid
