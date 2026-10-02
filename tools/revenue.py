"""知識検定対策ブログの年間収益をざっくり試算する。

使い方: python3 tools/revenue.py
前提の数字は SCENARIOS を書き換えて調整する。
"""

SCENARIOS = {
    # 月平均の検索数: キーワードプランナーの「知識 検定」= 1,000〜1万（幅）
    "悲観": dict(
        head_monthly=1_000,   # 「知識検定」の月平均検索数
        head_ctr=0.02,        # 「知識検定」で検索した人がブログを開く割合（公式サイトに大半が流れる）
        tail_ratio=0.2,       # 「知識検定 対策／過去問／難易度…」などの合計が「知識検定」の何割か
        tail_ctr=0.15,        # 関連キーワードで検索した人がブログを開く割合
        pv_per_visit=2.0,     # 1回の訪問で見るページ数
        rpm=150,              # 広告収益（円／1000PV）
        book_cvr=0.002,       # 訪問者が『知識検定事典』をリンク経由で買う割合
        paid_cvr=0.01,        # 訪問者が有料の想定問題集を買う割合
    ),
    "標準": dict(
        head_monthly=3_000, head_ctr=0.05, tail_ratio=0.3, tail_ctr=0.25,
        pv_per_visit=2.5, rpm=250, book_cvr=0.005, paid_cvr=0.01,
    ),
    "楽観": dict(
        head_monthly=10_000, head_ctr=0.10, tail_ratio=0.5, tail_ctr=0.30,
        pv_per_visit=3.0, rpm=400, book_cvr=0.01, paid_cvr=0.01,
    ),
}

BOOK_PRICE = 2_420        # 『知識検定事典』の定価（税込）
BOOK_RATE = 0.03          # 紙の本のアフィリエイト料率（目安。最新の料率は各サービスで確認）
PAID_PRICE = 500          # 有料の想定問題集（note など）の価格
PAID_NET = 0.855          # note でクレジットカード決済のときの手取り率の目安（決済手数料5%＋利用料10%）


def estimate(p):
    head_year = p["head_monthly"] * 12
    visits = head_year * p["head_ctr"] + head_year * p["tail_ratio"] * p["tail_ctr"]
    pv = visits * p["pv_per_visit"]
    ads = pv * p["rpm"] / 1000
    book = visits * p["book_cvr"] * BOOK_PRICE * BOOK_RATE
    paid_buyers = visits * p["paid_cvr"]
    paid = paid_buyers * PAID_PRICE * PAID_NET
    return dict(visits=visits, pv=pv, ads=ads, book=book, paid_buyers=paid_buyers, paid=paid)


if __name__ == "__main__":
    print(f"{'':6}{'年間訪問':>10}{'年間PV':>10}{'広告':>10}{'書籍リンク':>10}{'有料問題集':>12}{'(購入者)':>10}{'合計':>10}")
    for name, p in SCENARIOS.items():
        r = estimate(p)
        total = r["ads"] + r["book"] + r["paid"]
        print(f"{name:6}{r['visits']:>10,.0f}{r['pv']:>10,.0f}{r['ads']:>10,.0f}{r['book']:>10,.0f}"
              f"{r['paid']:>12,.0f}{r['paid_buyers']:>10,.0f}{total:>10,.0f}")
