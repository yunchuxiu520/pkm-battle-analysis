# pkm-battle-analysis

用公开对战数据做宝可梦（Gen 9 OU）使用率与配置分析——一个从数据到图表的完整小项目。

## 这是什么

Pokémon Showdown 天梯每场对局都会被统计，Smogon 每月把结果汇总成公开的 `chaos` JSON。
这个项目把这些数据读进 pandas，产出：

- 全分段 / 高分段使用率排行
- 单只宝可梦的道具、招式、特性搭配占比
- 队友搭配频率（谁和谁经常一起出现）

不依赖任何付费数据源，也不需要爬虫，全部来自官方公开统计。

## 数据来源

| 内容 | 地址 |
|---|---|
| 月度统计目录 | <https://www.smogon.com/stats/> |
| 单月单分段文件 | `https://www.smogon.com/stats/{YYYY-MM}/chaos/{格式}-{分段}.json` |

当前已下载（2026-10）：

- `gen9ou-0.json` — 全分段，8.5 MB
- `gen9ou-1500.json` — 1500 分以上，12 MB

> 国内直连 smogon 较慢，单个文件约 2~4 分钟，`src/fetch.py` 已做重试和断点跳过。

## 快速开始

```bash
# 1. 装依赖
pip install -r requirements.txt

# 2. 下载数据（已有 data/*.json 会跳过）
python -m src.fetch 2026-10

# 3. 出图，结果在 output/
python -m src.report
```

Windows 上如果在 PowerShell 里报编码错误，先执行 `chcp 65001`。

## 目录结构

```
pkm-battle-analysis/
├── data/                  # chaos json（体积大，可不入库）
├── src/
│   ├── fetch.py           # 下载 + 重试
│   ├── loader.py          # 读 json → pandas 表
│   └── report.py          # 出图 CLI
├── output/                # PNG + CSV
└── requirements.txt
```

## 已实现（阶段 1）

- [x] 数据下载与本地缓存
- [x] 使用率排行（408 只宝可梦）
- [x] 道具 / 招式 / 特性占比归一化
- [x] 性格与努力值配置拆解（`spread_table`）
- [x] 队友共现分析
- [x] 三张图的自动生成

## 路线图

- [ ] 阶段 2：属性克制矩阵 + 队伍弱点分析（纯逻辑，不依赖数据）
- [ ] 阶段 3：FastAPI 接口 + 网页前端，部署到公网
- [ ] 阶段 4：用 Showdown 回放日志训练"下一手预测"模型

## 踩过的坑

1. `chaos` 里 `Items` / `Moves` 的数值是**加权计数**，不是百分比，必须自己除以总和。
2. `usage` 在 `gen9ou-1500.json` 里是 float，在部分旧格式里是 dict，读取时要兼容。
3. `Spreads` 的键形如 `Jolly:252/252/0/0/4/0`，需要 `partition(":")` 拆开。
4. Abilities 通常只有一个选项，画条形图没有信息量，改用文字列表更清楚。