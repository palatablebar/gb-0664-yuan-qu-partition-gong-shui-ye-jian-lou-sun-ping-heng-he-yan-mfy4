# 深度登记 园区分区供水与夜间漏损核验

- 规模：中型
- 核心规则：以计量边为唯一事实归属分区，跨区转供在两侧分别记入并在全园合计相消；使用误差上下界判断漏损。

## 功能模块

| 模块 | 使用者动作 | 入口 | 核心文件 | 测试 |
|---|---|---|---|---|
| M1 计量采信 | 读取台账并核对原始列与行号 | `GET /api/intake` | `app/modules/m1_intake/service.py` `app/modules/m1_intake/rules.py` | `tests/test_intake.py` |
| M2 单位契约 | 将升与立方米统一并裁决重复键 | `GET /api/contract` | `app/modules/m2_contract/service.py` `app/modules/m2_contract/rules.py` | `tests/test_contract.py` |
| M3 拓扑归属 | 核查计量目录、方向、环与反向补流 | `GET /api/model` | `app/modules/m3_model/service.py` `app/modules/m3_model/rules.py` | `tests/test_model.py` `tests/test_reverse.py` |
| M4 水量平衡 | 计算各分区与夜间净水量 | `GET /api/calculate` | `app/modules/m4_calculate/service.py` `app/modules/m4_calculate/rules.py` | `tests/test_calculate.py` |
| M5 质量隔离 | 按原因码定位异常证据 | `GET /api/quarantine` | `app/modules/m5_quarantine/service.py` `app/modules/m5_quarantine/rules.py` | `tests/test_quarantine.py` |
| M6 阈值复核 | 复算误差上下界与水量守恒 | `GET /api/reconcile` | `app/modules/m6_reconcile/service.py` `app/modules/m6_reconcile/rules.py` | `tests/test_reconcile.py` |
| M7 批次归档 | 幂等重跑与版本复核 | `GET /api/batches` | `app/modules/m7_batches/service.py` `app/modules/m7_batches/rules.py` | `tests/test_batches.py` |

## 陷阱登记

| TRAP | 现象 | 朴素实现会怎样 | 本项目处理 | 处理位置 | 测试 |
|---|---|---|---|---|---|
| TRAP-01 | 混合编码 | 静默误算或覆盖证据 | UTF8优先，GB18030回退 | `app/modules/m1_intake/rules.py` | `tests/test_intake.py::test_gb18030` |
| TRAP-02 | 首列BOM | 静默误算或覆盖证据 | utf-8-sig解码 | `app/modules/m1_intake/rules.py` | `tests/test_intake.py::test_bom_header` |
| TRAP-06 | 全角与千分位 | 静默误算或覆盖证据 | NFKC后Decimal解析 | `app/modules/m2_contract/rules.py` | `tests/test_contract.py::test_fullwidth` |
| TRAP-07 | 空值哨兵 | 静默误算或覆盖证据 | 隔离而非置零 | `app/modules/m2_contract/rules.py` | `tests/test_contract.py::test_null` |
| TRAP-10 | 浮点精度 | 静默误算或覆盖证据 | Decimal守恒 | `app/modules/m4_calculate/rules.py` | `tests/test_calculate.py::test_decimal_conservation` |
| TRAP-14 | 重复键异值 | 静默误算或覆盖证据 | 相同取首条，冲突全部隔离 | `app/modules/m2_contract/rules.py` | `tests/test_contract.py::test_conflict` |
| TRAP-15 | 升与立方米混用 | 静默误算或覆盖证据 | 显式单位乘数 | `app/modules/m2_contract/rules.py` | `tests/test_contract.py::test_units` |
| TRAP-20 | 拓扑循环 | 静默误算或覆盖证据 | DFS返回环路径 | `app/modules/m3_model/rules.py` | `tests/test_model.py::test_cycle` |
| TRAP-21 | 流向关系不一致 | 静默误算或覆盖证据 | 目录和台账双向字段比对，反向行细分DIRECTION | `app/modules/m3_model/rules.py` | `tests/test_model.py::test_bad_direction` |
| TRAP-27 | 反向补流与方向异常混淆 | 照目录则分区失真，全信现场则掩盖漏损 | 转供边+夜间窗口+抢修工单齐备才按现场方向入账，否则DIRECTION隔离 | `app/modules/m3_model/rules.py` | `tests/test_reverse.py::test_reverse_without_order_is_anomaly` |
| TRAP-23 | 夜间边界 | 静默误算或覆盖证据 | 当地00:00含、05:00不含 | `app/modules/m4_calculate/rules.py` | `tests/test_calculate.py::test_night_boundary` |
| TRAP-26 | 陈旧复核 | 静默误算或覆盖证据 | 条件更新修订号 | `app/modules/m7_batches/rules.py` | `tests/test_batches.py::test_stale` |

## 对账规则
输入行数=有效行+隔离行+空行。供水量=售水量+授权用水+各区残差。value为原值，unit支持m3与L，value_m3为立方米。error_pct在0至10之间，误差按每条计量绝对值相加；不假设独立随机误差。时间必须含偏移，先转UTC；夜间为中国标准时间[00:00,05:00)。

## 已知不覆盖
不推断缺失表的读数，不做管网压力仿真。计量目录只允许无环转供，复杂回流管网需先另建可辨识模型。
