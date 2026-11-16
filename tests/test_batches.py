import pytest
from app.modules.m7_batches.service import run
from app.modules.m7_batches.rules import csv_evidence
from app.store import history,review,fetch
from app.errors import DomainError
def test_idempotent(dirty):a=run(dirty);b=run(dirty);assert a["manifest"]["run_id"]==b["manifest"]["run_id"];assert len(history())==1
def test_params_key(clean):assert run(clean)["manifest"]["run_id"]!=run({"sample":"clean","params":{"threshold":"2"}})["manifest"]["run_id"]
def test_review(dirty):a=run(dirty);b=review(a["manifest"]["run_id"],1,"通过");assert b["revision"]==2
def test_stale(dirty): # TRAP-26
    a=run(dirty);review(a["manifest"]["run_id"],1,"通过")
    with pytest.raises(DomainError,match="重新载入"):review(a["manifest"]["run_id"],1,"退回")
def test_export(dirty):assert "DUPLICATE" in csv_evidence(run(dirty))
def test_saved_exact(clean):a=run(clean);assert fetch(a["manifest"]["run_id"])["reconciliation"]["residual"]=="690.000"
def test_parameter():
    with pytest.raises(DomainError):run({"sample":"../../wrong"})
def test_equivalent_threshold_is_same_key(dirty):
    a=run(dirty);b=run({"sample":"dirty","params":{"threshold":5}});c=run({"sample":"dirty","params":{"threshold":"5.0"}})
    assert a["manifest"]["run_id"]==b["manifest"]["run_id"]==c["manifest"]["run_id"]
def test_equal_content_is_same_key(dirty):
    from app.modules.m1_intake.service import source
    a=run(dirty);b=run({"text":source(dirty).decode("utf-8")})
    assert a["manifest"]["run_id"]==b["manifest"]["run_id"]

def test_review_rejects_structured_parameters(dirty):
    a=run(dirty);rid=a["manifest"]["run_id"]
    with pytest.raises(DomainError):review(rid,[],"通过")
    with pytest.raises(DomainError):review(rid,1,[])
