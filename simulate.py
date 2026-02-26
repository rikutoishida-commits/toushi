"""
投資リターンシミュレーション
基準日: 2026/2/1
期間: 過去5年間 (2021/2/1 〜 2026/2/1)
投資方法: 一括投資 100万円
対象: S&P500 / 金(ゴールド)
"""

import csv
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "simulation_result.png")

INITIAL_INVESTMENT = 1_000_000  # 100万円
START_DATE = datetime(2021, 2, 1)
END_DATE = datetime(2026, 2, 1)


def load_sp500(path: str) -> list[tuple[datetime, float]]:
    """S&P500.csv を読み込み、(日付, 資産値) のリストを返す"""
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダー読み飛ばし
        for row in reader:
            dt = datetime.strptime(row[0], "%Y%m%d")
            value = float(row[1])
            rows.append((dt, value))
    return rows


def load_gold(path: str) -> list[tuple[datetime, float]]:
    """gold.csv を読み込み、(日付, 資産値) のリストを返す"""
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダー行1
        next(reader)  # ヘッダー行2
        for row in reader:
            dt = datetime.strptime(row[0], "%Y/%m/%d")
            value = float(row[1])
            rows.append((dt, value))
    return rows


def filter_period(data, start, end):
    """指定期間のデータを抽出"""
    return [(dt, v) for dt, v in data if start <= dt <= end]


def simulate_lump_sum(data, investment):
    """
    一括投資シミュレーション
    初日の資産値を基準に、各日の評価額を計算
    """
    base_value = data[0][1]
    results = []
    for dt, v in data:
        current_value = investment * (v / base_value)
        results.append((dt, current_value))
    return results


def format_yen(x, _):
    """円表示フォーマッタ（万円単位）"""
    man = x / 10000
    if man >= 100:
        return f"¥{man:.0f}M"
    return f"¥{man:.0f}M"


def main():
    # データ読み込み
    sp500_all = load_sp500(os.path.join(DATA_DIR, "S&P500.csv"))
    gold_all = load_gold(os.path.join(DATA_DIR, "gold.csv"))

    # 期間フィルタ
    sp500 = filter_period(sp500_all, START_DATE, END_DATE)
    gold = filter_period(gold_all, START_DATE, END_DATE)

    if not sp500 or not gold:
        print("エラー: 指定期間のデータが見つかりません")
        return

    # シミュレーション実行
    sp500_sim = simulate_lump_sum(sp500, INITIAL_INVESTMENT)
    gold_sim = simulate_lump_sum(gold, INITIAL_INVESTMENT)

    # --- 結果サマリー ---
    sp500_start = sp500_sim[0]
    sp500_end = sp500_sim[-1]
    gold_start = gold_sim[0]
    gold_end = gold_sim[-1]

    sp500_return = (sp500_end[1] / INITIAL_INVESTMENT - 1) * 100
    gold_return = (gold_end[1] / INITIAL_INVESTMENT - 1) * 100

    print("=" * 55)
    print("  投資リターンシミュレーション結果")
    print(f"  期間: {START_DATE:%Y/%m/%d} → {sp500_end[0]:%Y/%m/%d}")
    print(f"  初期投資額: ¥{INITIAL_INVESTMENT:,.0f}")
    print("=" * 55)
    print()
    print(f"  【S&P500】")
    print(f"    最終評価額: ¥{sp500_end[1]:,.0f}")
    print(f"    損益:       ¥{sp500_end[1] - INITIAL_INVESTMENT:+,.0f}")
    print(f"    リターン:   {sp500_return:+.1f}%")
    print()
    print(f"  【金(ゴールド)】")
    print(f"    最終評価額: ¥{gold_end[1]:,.0f}")
    print(f"    損益:       ¥{gold_end[1] - INITIAL_INVESTMENT:+,.0f}")
    print(f"    リターン:   {gold_return:+.1f}%")
    print()

    # 最高値・最安値
    sp500_max = max(sp500_sim, key=lambda x: x[1])
    sp500_min = min(sp500_sim, key=lambda x: x[1])
    gold_max = max(gold_sim, key=lambda x: x[1])
    gold_min = min(gold_sim, key=lambda x: x[1])

    print("-" * 55)
    print(f"  【S&P500 レンジ】")
    print(f"    最高値: ¥{sp500_max[1]:,.0f} ({sp500_max[0]:%Y/%m/%d})")
    print(f"    最安値: ¥{sp500_min[1]:,.0f} ({sp500_min[0]:%Y/%m/%d})")
    print(f"  【金 レンジ】")
    print(f"    最高値: ¥{gold_max[1]:,.0f} ({gold_max[0]:%Y/%m/%d})")
    print(f"    最安値: ¥{gold_min[1]:,.0f} ({gold_min[0]:%Y/%m/%d})")
    print("=" * 55)

    # --- グラフ作成 ---
    plt.rcParams["font.size"] = 11

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), height_ratios=[3, 1])
    fig.suptitle(
        f"Lump Sum Investment Simulation: {START_DATE:%Y/%m/%d} - {sp500_end[0]:%Y/%m/%d}\n"
        f"Initial Investment: ¥{INITIAL_INVESTMENT:,.0f}",
        fontsize=14,
        fontweight="bold",
    )

    # --- 上段: 評価額推移 ---
    dates_sp = [d for d, _ in sp500_sim]
    vals_sp = [v for _, v in sp500_sim]
    dates_gd = [d for d, _ in gold_sim]
    vals_gd = [v for _, v in gold_sim]

    ax1.plot(dates_sp, vals_sp, label="S&P500", color="#1f77b4", linewidth=1.5)
    ax1.plot(dates_gd, vals_gd, label="Gold", color="#d4af37", linewidth=1.5)
    ax1.axhline(y=INITIAL_INVESTMENT, color="gray", linestyle="--", alpha=0.6, label="Initial (¥1,000,000)")

    ax1.set_ylabel("Portfolio Value (JPY)")
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_yen))
    ax1.legend(loc="upper left", fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # 最終値をアノテーション
    ax1.annotate(
        f"S&P500: ¥{sp500_end[1]:,.0f}\n({sp500_return:+.1f}%)",
        xy=(sp500_end[0], sp500_end[1]),
        xytext=(-120, 20),
        textcoords="offset points",
        fontsize=9,
        color="#1f77b4",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#1f77b4", alpha=0.7),
    )
    ax1.annotate(
        f"Gold: ¥{gold_end[1]:,.0f}\n({gold_return:+.1f}%)",
        xy=(gold_end[0], gold_end[1]),
        xytext=(-120, -30),
        textcoords="offset points",
        fontsize=9,
        color="#d4af37",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#d4af37", alpha=0.7),
    )

    # --- 下段: 日次リターン率推移 ---
    sp500_pct = [(dates_sp[i], (vals_sp[i] / INITIAL_INVESTMENT - 1) * 100) for i in range(len(vals_sp))]
    gold_pct = [(dates_gd[i], (vals_gd[i] / INITIAL_INVESTMENT - 1) * 100) for i in range(len(vals_gd))]

    ax2.plot([d for d, _ in sp500_pct], [v for _, v in sp500_pct], color="#1f77b4", linewidth=1, alpha=0.8)
    ax2.plot([d for d, _ in gold_pct], [v for _, v in gold_pct], color="#d4af37", linewidth=1, alpha=0.8)
    ax2.axhline(y=0, color="gray", linestyle="--", alpha=0.6)
    ax2.set_ylabel("Return (%)")
    ax2.set_xlabel("Date")
    ax2.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
    print(f"\nGraph saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
