import pytest
from app.modules.m3_model.service import run
from app.modules.m3_model.rules import cycle_path,validate_catalog,match
from app.errors import DomainError
def test_zones(clean):assert run(clean)["zones"]==["A","B","C"]
def test_bad_direction(dirty): # TRAP-21
    assert "REFERENCE" in [x["code"] for x in run(dirty)["quarantine"]]
def test_valid_count(dirty):assert len(run(dirty)["rows"])==54
def test_catalog(clean):assert run(clean)["catalog"]["AB"]==["A","B","transfer"]
def test_cycle(): # TRAP-20
    assert cycle_path([("A","B"),("B","A")])==["A","B","A"]
def test_cycle_rejected():
    with pytest.raises(DomainError,match="存在环"):validate_catalog({"1":["A","B","transfer"],"2":["B","A","transfer"]})
def test_self_loop():
    with pytest.raises(DomainError,match="自环"):validate_catalog({"1":["A","A","transfer"]})
