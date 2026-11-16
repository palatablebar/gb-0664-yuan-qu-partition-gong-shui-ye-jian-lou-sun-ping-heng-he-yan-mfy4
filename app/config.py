from pathlib import Path
import os
TITLE='分区水量核对'
RULE_VERSION="2026.11.3"
SAMPLE_DIR=Path(__file__).resolve().parent.parent/"sample_data"
SAMPLES=("dirty","clean","gb18030","night")
MODULES=[('intake', '计量采信'), ('contract', '单位契约'), ('model', '拓扑归属'), ('calculate', '水量平衡'), ('quarantine', '质量隔离'), ('reconcile', '阈值复核'), ('batches', '批次归档')]
SENTINELS={"", "-", "N/A", "NULL", "未知"}
def data_dir():
    return Path(os.environ.get("DATA_DIR", "./var"))
