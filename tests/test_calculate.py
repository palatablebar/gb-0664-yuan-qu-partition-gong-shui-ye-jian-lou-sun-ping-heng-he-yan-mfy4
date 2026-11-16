from decimal import Decimal
from app.modules.m4_calculate.service import run
from app.modules.m4_calculate.rules import balances,night
def test_a_residual(clean):assert run(clean)["results"][0]["residual"]=="480.000"
def test_b_residual(clean):assert run(clean)["results"][1]["residual"]=="180"
def test_c_residual(dirty):assert Decimal(run(dirty)["results"][2]["residual"])==30
def test_uncertainty(clean):assert Decimal(run(clean)["results"][0]["uncertainty"])==Decimal("57.6")
def test_night_equals(clean):assert run(clean)["night_results"]==run(clean)["results"]
def test_night_boundary(): # TRAP-23
    assert night("2026-11-01T20:59:59+00:00");assert not night("2026-11-01T21:00:00+00:00")
def test_decimal_conservation(clean): # TRAP-10
    assert sum((Decimal(x["residual"]) for x in run(clean)["results"]),Decimal(0))==690
