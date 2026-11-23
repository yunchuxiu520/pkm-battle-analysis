"""数据加载与清洗：把 Smogon 月度对战统计读成 pandas 表。"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def load_chaos(path: str | Path) -> dict:
    """读一份 chaos json，返回 {"info": 元信息, "data": 原始字典}。"""
    path = Path(path)
    if not path.is_absolute():
        path = DATA_DIR / path
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return raw


def usage_table(chaos: dict) -> pd.DataFrame:
    """把每只宝可梦的使用率抽成一张表，按使用率降序。

    列: name / usage / raw_count
    usage 已经是 0~1 的比例，raw_count 是加权出现次数。
    """
    rows = []
    for name, mon in chaos["data"].items():
        rows.append(
            {
                "name": name,
                "usage": float(mon["usage"]),
                "raw_count": int(mon.get("Raw count", 0)),
            }
        )
    df = pd.DataFrame(rows).sort_values("usage", ascending=False).reset_index(drop=True)
    df.index += 1  # 排名从 1 开始
    return df


def breakdown(mon: dict, key: str) -> pd.Series:
    """把 Items / Moves / Abilities / Tera Types 之类的权重归一成 0~1 占比。

    chaos 里的值是该配置的加权计数，不是百分比，所以要自己除以总和。
    """
    counts = mon.get(key) or {}
    total = sum(counts.values())
    if total <= 0:
        return pd.Series(dtype="float64")
    s = pd.Series({k: v / total for k, v in counts.items()})
    return s.sort_values(ascending=False)


def spread_table(mon: dict, top: int = 5) -> pd.DataFrame:
    """性格/努力值配置：chaos 的键形如 "Jolly:252/252/0/0/4/0"。

    拆成 nature / evs 两列，方便按性格聚合。
    """
    spreads = mon.get("Spreads") or {}
    total = sum(spreads.values()) or 1
    rows = []
    for k, v in spreads.items():
        nature, _, evs = k.partition(":")
        rows.append({"nature": nature or k, "evs": evs, "share": v / total})
    df = pd.DataFrame(rows).sort_values("share", ascending=False)
    return df.head(top).reset_index(drop=True)


def teammate_table(chaos: dict, name: str, top: int = 10) -> pd.DataFrame:
    """队友分析：和某只宝可梦同队出现频率最高的伙伴。

    chaos 的 Teammates 给的是与它同队的加权计数，除以它自身的 raw_count
    可以近似成"带这只时有多少比例会带某队友"。
    """
    mon = chaos["data"][name]
    mates = mon.get("Teammates") or {}
    base = max(int(mon.get("Raw count", 0)), 1)
    rows = [
        {"teammate": k, "co_rate": v / base}
        for k, v in mates.items()
        if k in chaos["data"]
    ]
    return (
        pd.DataFrame(rows)
        .sort_values("co_rate", ascending=False)
        .head(top)
        .reset_index(drop=True)
    )