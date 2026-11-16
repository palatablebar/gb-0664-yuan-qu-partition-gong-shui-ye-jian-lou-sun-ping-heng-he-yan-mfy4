import pytest
from app.modules.m1_intake.service import run,source
from app.modules.m1_intake.rules import read,COLUMNS
from app.errors import DomainError
def test_dirty_count(dirty):assert run(dirty)["input_count"]==59
def test_clean_count(clean):assert len(run(clean)["rows"])==54
def test_bom_header(dirty): # TRAP-02
    assert run(dirty)["rows"][0]["record_id"]=="01-IN-A"
def test_gb18030(): # TRAP-01
    assert run({"sample":"gb18030"})["encoding"]=="gb18030"
def test_bad_column(dirty):assert run(dirty)["quarantine"][0]["code"]=="COLUMN_COUNT"
def test_empty():
    with pytest.raises(DomainError,match="文件为空"):read(b"")
def test_multiline_record():
    text=",".join(COLUMNS)+'\n001,2026-11-01T00:00:00Z,"AA\nBB",A,B,transfer,1,m3,1\n'
    assert read(text.encode())["rows"][0]["meter"]=="AA\nBB"
