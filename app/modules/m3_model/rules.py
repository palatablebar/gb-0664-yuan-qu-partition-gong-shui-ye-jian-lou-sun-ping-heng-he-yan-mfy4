from app.errors import reject
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
