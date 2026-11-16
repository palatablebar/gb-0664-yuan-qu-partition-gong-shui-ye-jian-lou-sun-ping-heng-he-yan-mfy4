from decimal import Decimal
import pytest
from app.modules.m2_contract.service import run
from app.modules.m2_contract.rules import number,normalize,deduplicate
from app.modules.m1_intake.service import run as ingest
from app.errors import DomainError
def test_units(clean): # TRAP-15
    assert next(x for x in run(clean)["rows"] if x["meter"]=="AC")["value_m3"]=="200.000"
def test_fullwidth(): # TRAP-06
    assert number("１，２３４．５")==Decimal("1234.5")
def test_null(dirty): # TRAP-07
    assert "MISSING" in [x["code"] for x in run(dirty)["quarantine"]]
def test_negative(dirty):assert "NEGATIVE" in [x["code"] for x in run(dirty)["quarantine"]]
def test_duplicate(dirty): # TRAP-14
    assert len([x for x in run(dirty)["quarantine"] if x["code"]=="DUPLICATE"])==1
def test_conflict(clean):
    a=run(clean)["rows"][0];b={**a,"value_m3":"99","line":100};good,bad=deduplicate([a,b]);assert good==[];assert len(bad)==2
def test_finite():
    with pytest.raises(DomainError):number("NaN")
