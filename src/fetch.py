"""下载 Smogon 月度对战数据。

用法:
    python -m src.fetch 2026-10 gen9ou-1500.json
    python -m src.fetch 2026-10          # 默认抓几档常用分段

国内直连 smogon 比较慢（单个文件 2~4 分钟），代码里做了重试和断点跳过。
"""
from __future__ import annotations

import sys
import time
import urllib.request
from pathlib import Path

from .loader import DATA_DIR

BASE = "https://www.smogon.com/stats/{month}/chaos/{fname}"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) pkm-study/1.0"}
DEFAULT_FILES = ["gen9ou-0.json", "gen9ou-1500.json"]


def download(month: str, fname: str, retries: int = 3) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / fname
    if out.exists() and out.stat().st_size > 100_000:
        print(f"[skip] {out.name} 已存在 ({out.stat().st_size/1e6:.1f}MB)")
        return out

    url = BASE.format(month=month, fname=fname)
    for i in range(1, retries + 1):
        try:
            t0 = time.time()
            print(f"[get ] {url}  第 {i} 次尝试…")
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                blob = r.read()
            out.write_bytes(blob)
            print(f"[ok  ] {out.name}  {len(blob)/1e6:.2f}MB  {time.time()-t0:.0f}s")
            return out
        except Exception as e:  # noqa: BLE001
            print(f"[fail] {type(e).__name__}: {e}")
            time.sleep(3 * i)
    raise SystemExit(f"下载失败: {url}")


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit("用法: python -m src.fetch <YYYY-MM> [文件名…]")
    month = argv[0]
    files = argv[1:] or DEFAULT_FILES
    for f in files:
        download(month, f)


if __name__ == "__main__":
    main(sys.argv[1:])