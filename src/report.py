"""阶段 1 产出：使用率排行 + 单只宝可梦配置拆解，全部落成 PNG。

用法:
    python -m src.report                 # 默认读 gen9ou-1500.json
    python -m src.report gen9ou-0.json   # 换低分段数据
"""
from __future__ import annotations

import sys

import matplotlib

matplotlib.use("Agg")  # 无窗口环境也要能出图
import matplotlib.pyplot as plt  # noqa: E402

from .loader import ROOT, breakdown, load_chaos, teammate_table, usage_table  # noqa: E402

OUT = ROOT / "output"
ACCENT = "#2f6f4f"
GREY = "#8a8f8c"


def fig_top_usage(chaos: dict, n: int = 20):
    df = usage_table(chaos).head(n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 7.5))
    bars = ax.barh(df["name"], df["usage"] * 100, color=ACCENT, height=0.72)
    top = df["usage"].iloc[-1] * 100
    for b, v in zip(bars, df["usage"] * 100):
        ax.text(v + 0.25, b.get_y() + b.get_height() / 2, f"{v:.1f}%",
                va="center", fontsize=8, color="#333")
    ax.set_xlabel("Usage on ladder (%)")
    ax.set_title(f"Top {n} usage — {chaos['info']['metagame']} "
                 f"@{chaos['info']['cutoff']}\n{chaos['info']['number of battles']:,} battles",
                 fontsize=11, loc="left")
    ax.set_xlim(0, top * 1.12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", labelsize=9)
    fig.tight_layout()
    return fig


def fig_loadout(chaos: dict, name: str, top: int = 6):
    """道具 / 技能 / 特性三栏。每栏按自己的最大值缩放，避免共用 0-100 轴浪费版面。

    Abilities 常常只有一个选项（100%），画条形没有信息量，改用文字列表。
    """
    mon = chaos["data"][name]
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2))

    for ax, (key, label) in zip(axes[:2], [("Items", "Item"), ("Moves", "Move")]):
        s = breakdown(mon, key).head(top).iloc[::-1]
        bars = ax.barh([k.replace("-", " ") for k in s.index], s.values * 100,
                       color=ACCENT if key == "Items" else GREY, height=0.65)
        vmax = max(s.values * 100) if len(s) else 100
        for b, v in zip(bars, s.values * 100):
            ax.text(v + vmax * 0.02, b.get_y() + b.get_height() / 2,
                    f"{v:.0f}%", va="center", fontsize=8)
        ax.set_title(f"{label}  (top {top})", fontsize=10, loc="left")
        ax.set_xlim(0, vmax * 1.18)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=8)

    ax = axes[2]
    s = breakdown(mon, "Abilities")
    ax.axis("off")
    ax.set_title("Ability", fontsize=10, loc="left")
    if len(s) == 1:
        only, share = s.index[0], s.iloc[0]
        ax.text(0, 0.88, only.replace("-", " "), fontsize=13, color=ACCENT, weight="bold")
        ax.text(0, 0.74, f"{share*100:.0f}% of sets — the only ability in use",
                fontsize=8.5, color=GREY)
    else:
        y = 0.9
        for k, v in s.head(top).items():
            ax.text(0, y, f"{k.replace('-', ' ')}", fontsize=9)
            ax.text(0.9, y, f"{v*100:.0f}%", fontsize=9, ha="right")
            y -= 0.14

    fig.suptitle(f"{name} — loadout @{chaos['info']['cutoff']}", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    return fig


def fig_teammates(chaos: dict, name: str, top: int = 12):
    df = teammate_table(chaos, name, top).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    ax.barh(df["teammate"], df["co_rate"] * 100, color=GREY, height=0.68)
    for i, v in enumerate(df["co_rate"] * 100):
        ax.text(v + 0.3, i, f"{v:.0f}%", va="center", fontsize=8)
    ax.set_xlabel("Chance to be on the same team (%)")
    ax.set_title(f"Teammates of {name}", fontsize=11, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()
    return fig


def main(argv: list[str]) -> None:
    fname = argv[0] if argv else "gen9ou-1500.json"
    chaos = load_chaos(fname)
    OUT.mkdir(parents=True, exist_ok=True)

    df = usage_table(chaos)
    df.to_csv(OUT / "usage_ranking.csv", encoding="utf-8-sig")
    print(f"[ok] 使用率表 -> output/usage_ranking.csv  ({len(df)} 只)")

    star = df["name"].iloc[0]
    fig_loadout(chaos, star).savefig(OUT / "loadout_top1.png", dpi=130)
    print(f"[ok] 使用率第一 {star} 的配置图 -> output/loadout_top1.png")

    fig_top_usage(chaos).savefig(OUT / "top20_usage.png", dpi=130)
    print("[ok] Top20 使用率图 -> output/top20_usage.png")

    fig_teammates(chaos, star).savefig(OUT / "teammates_top1.png", dpi=130)
    print(f"[ok] {star} 的队友图 -> output/teammates_top1.png")


if __name__ == "__main__":
    main(sys.argv[1:])