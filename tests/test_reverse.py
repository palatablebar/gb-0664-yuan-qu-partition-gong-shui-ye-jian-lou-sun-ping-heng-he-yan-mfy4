import pytest
from decimal import Decimal
from app.modules.m3_model.rules import validate_repair_orders,reversed_match,order_for,night
from app.modules.m4_calculate.service import run as calculate
from app.modules.m6_reconcile.service import run as reconcile
from app.modules.m7_batches.service import run
from app.modules.m7_batches.rules import csv_evidence
from app.store import history,review,fetch
from app.errors import DomainError
CATALOG={"AB":["A","B","transfer"],"SA":["A","OUT","sale"]}
def test_reverse_accepted_with_order(night):
    result=calculate(night)
    flows=result["reverse_flows"]
    assert len(flows)==1 and flows[0]["meter"]=="AB" and flows[0]["from_zone"]=="B" and flows[0]["to_zone"]=="A"
    assert flows[0]["value_m3"]=="120" and flows[0]["order_date"]=="2026-11-07"
    assert any(row["meter"]=="AB" and row["from_zone"]=="B" for row in result["rows"])
def test_reverse_without_order_is_anomaly(night):
    codes=[x["code"] for x in calculate(night)["quarantine"]]
    assert codes.count("DIRECTION")==2 # 夜间无工单与白天反向均不得当作补流
def test_reverse_balance(night):
    results={x["zone"]:x for x in calculate(night)["results"]}
    assert Decimal(results["A"]["residual"])==280 # 含补流流入120，两侧分别入账
    assert Decimal(results["B"]["residual"])==-60
def test_night_conclusions(night):
    results={x["zone"]:x for x in reconcile(night)["night_results"]}
    assert Decimal(results["A"]["residual"])==580 and results["A"]["status"]=="漏损"
    assert Decimal(results["B"]["residual"])==-360 and results["B"]["status"]=="倒挂"
    assert results["C"]["status"]=="漏损"
def test_conservation_with_reverse(night):
    data=reconcile(night)
    assert data["reconciliation"]["balanced"] is True
    assert Decimal(data["reconciliation"]["residual"])==230
def test_retry_not_counted_twice(night):
    a=run(night);b=run(night)
    assert a["manifest"]["run_id"]==b["manifest"]["run_id"] and len(history())==1
    codes=[x["code"] for x in a["quarantine"]]
    assert codes.count("DUPLICATE")==1 # 同一记录重试只计一次
    assert {x["zone"]:x for x in a["results"]}["A"]["inflow"]=="2120"
def test_publish_failure_keeps_old(night):
    a=run(night);rid=a["manifest"]["run_id"]
    review(rid,1,"通过")
    with pytest.raises(DomainError,match="重新载入"):review(rid,1,"退回")
    kept=fetch(rid)
    assert kept["decision"]=="通过" and kept["revision"]==2
    assert len(kept["reverse_flows"])==1 and kept["rows"]
def test_order_validation():
    validate_repair_orders([{"meter":"AB","date":"2026-11-07"}],CATALOG)
    with pytest.raises(DomainError):validate_repair_orders([{"meter":"SA","date":"2026-11-07"}],CATALOG) # 非转供边
    with pytest.raises(DomainError):validate_repair_orders([{"meter":"AB","date":"不是日期"}],CATALOG)
    with pytest.raises(DomainError):validate_repair_orders([{"meter":"AB","date":"2026-11-07"},{"meter":"AB","date":"2026-11-07"}],CATALOG) # 重复工单
def test_reversed_match_only_transfer():
    row={"meter":"AB","from_zone":"B","to_zone":"A","kind":"transfer"}
    assert reversed_match(row,CATALOG) is True
    assert reversed_match({**row,"kind":"sale"},CATALOG) is False
    assert reversed_match({"meter":"SA","from_zone":"OUT","to_zone":"A","kind":"sale"},CATALOG) is False
def test_order_matches_cst_day():
    orders=[{"meter":"AB","date":"2026-11-07","note":""}]
    assert order_for(orders,"AB","2026-11-06T16:30:00+00:00") is not None # UTC入夜即CST 11-07
    assert order_for(orders,"AB","2026-11-08T16:30:00+00:00") is None
    assert night("2026-11-06T16:30:00+00:00") and not night("2026-11-07T10:00:00+00:00")
def test_evidence_includes_reverse(night):
    assert "REVERSE_MAKEUP" in csv_evidence(run(night))
