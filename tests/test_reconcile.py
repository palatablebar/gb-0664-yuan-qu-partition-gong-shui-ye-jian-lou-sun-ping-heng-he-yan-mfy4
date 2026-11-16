from decimal import Decimal
import pytest
from app.modules.m6_reconcile.service import run
from app.modules.m6_reconcile.rules import classify
from app.errors import DomainError
def test_supply(clean):assert run(clean)["reconciliation"]["supply"]=="6000"
def test_sales(clean):assert run(clean)["reconciliation"]["sales"]=="5100"
def test_authorized(clean):assert run(clean)["reconciliation"]["authorized"]=="210"
def test_mass(dirty):assert run(dirty)["reconciliation"]["balanced"] is True
def test_count(dirty):assert run(dirty)["reconciliation"]["count_ok"] is True
def test_leak(dirty):assert run(dirty)["results"][0]["status"]=="漏损"
def test_negative_threshold():
    with pytest.raises(DomainError):classify({"lower":"1","upper":"3","residual":"2"},"-1")
