"""questions/yosou.csv をチェックし、読みやすい一覧 questions/yosou.md を作る。

使い方: python3 tools/build.py
エラーがあれば一覧は作らずに終了する。警告（Xの文字数制限など）は表示だけする。
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "questions" / "yosou.csv"
OUT = ROOT / "questions" / "yosou.md"

GENRES = ["ことば", "地理・歴史", "政治・経済", "社会", "国際", "自然科学", "生活", "スポーツ", "芸術", "カルチャー"]
INDICATORS = ["基礎学力", "社会生活力", "語彙力", "推察力", "分析力", "時事力"]
LEVELS = {"A": "基礎", "B": "標準", "C": "難"}
STATUSES = ["下書き", "確認済", "要修正", "採用", "不採用"]
COLUMNS = ["ID", "バッチ", "ジャンル", "指標", "難易度", "問題文", "選択肢1", "選択肢2", "選択肢3", "選択肢4",
           "正解", "解説", "出典URL", "時点", "ステータス", "作問者", "X投稿日", "X正答率"]

X_CHOICE_MAX = 25   # Xの投票の選択肢は25文字まで
X_POST_MAX = 140    # 全角だけの投稿は140文字まで（ハッシュタグ込み）
HASHTAGS = " #知識検定 #{genre}"


def load():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in reader.fieldnames]
        if missing:
            sys.exit(f"列が足りません: {missing}")
        return list(reader)


def check(rows):
    errors, warnings = [], []
    ids = Counter(r["ID"] for r in rows)
    for qid, n in ids.items():
        if n > 1:
            errors.append(f"{qid}: IDが重複しています")
    for r in rows:
        qid = r["ID"]
        choices = [r[f"選択肢{i}"].strip() for i in range(1, 5)]
        if r["ジャンル"] not in GENRES:
            errors.append(f"{qid}: ジャンル「{r['ジャンル']}」は10ジャンルにありません")
        if r["指標"] not in INDICATORS:
            errors.append(f"{qid}: 指標「{r['指標']}」は未定義です（{'/'.join(INDICATORS)}）")
        if r["難易度"] not in LEVELS:
            errors.append(f"{qid}: 難易度はA/B/Cのどれかにしてください")
        if r["ステータス"] not in STATUSES:
            errors.append(f"{qid}: ステータスは{'/'.join(STATUSES)}のどれかにしてください")
        if r["正解"] not in {"1", "2", "3", "4"}:
            errors.append(f"{qid}: 正解は1〜4の番号で書いてください")
        if not r["問題文"].strip():
            errors.append(f"{qid}: 問題文が空です")
        if any(not c for c in choices):
            errors.append(f"{qid}: 空の選択肢があります")
        elif len(set(choices)) < 4:
            errors.append(f"{qid}: 同じ選択肢が重複しています")
        for i, c in enumerate(choices, 1):
            if len(c) > X_CHOICE_MAX:
                warnings.append(f"{qid}: 選択肢{i}が{len(c)}文字（Xの投票は{X_CHOICE_MAX}文字まで）")
        post_len = len(r["問題文"]) + len(HASHTAGS.format(genre=r["ジャンル"].replace("・", "")))
        if post_len > X_POST_MAX:
            warnings.append(f"{qid}: ハッシュタグ込みで{post_len}文字（Xは全角{X_POST_MAX}文字まで）")
    return errors, warnings


def summary(rows):
    lines = ["## 集計", "", "| ジャンル | 問題数 | A | B | C | 採用 | 確認済 | 下書き | 要修正 | 不採用 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for g in GENRES:
        rs = [r for r in rows if r["ジャンル"] == g]
        lv = Counter(r["難易度"] for r in rs)
        st = Counter(r["ステータス"] for r in rs)
        lines.append(f"| {g} | {len(rs)} | {lv['A']} | {lv['B']} | {lv['C']} | {st['採用']} | {st['確認済']} | "
                     f"{st['下書き']} | {st['要修正']} | {st['不採用']} |")
    lv = Counter(r["難易度"] for r in rows)
    st = Counter(r["ステータス"] for r in rows)
    lines.append(f"| **合計** | **{len(rows)}** | {lv['A']} | {lv['B']} | {lv['C']} | {st['採用']} | {st['確認済']} | "
                 f"{st['下書き']} | {st['要修正']} | {st['不採用']} |")
    pos = Counter(r["正解"] for r in rows)
    ind = Counter(r["指標"] for r in rows)
    lines += ["", "正解の位置：" + "／".join(f"{p}番 {pos[p]}問" for p in "1234"),
              "", "指標：" + "／".join(f"{i} {ind[i]}問" for i in INDICATORS if ind[i])]
    return lines


def render(rows):
    out = ["# 想定問題 一覧", "",
           "> このファイルは `python3 tools/build.py` で `questions/yosou.csv` から自動生成しています。直接編集しないでください。",
           ""]
    out += summary(rows)
    for g in GENRES:
        rs = [r for r in rows if r["ジャンル"] == g]
        if not rs:
            continue
        out += ["", f"## {g}（{len(rs)}問）"]
        for r in rs:
            ans = int(r["正解"])
            meta = f"{LEVELS[r['難易度']]}・{r['指標']}"
            if r["時点"]:
                meta += f"・{r['時点']}時点"
            out += ["", f"### {r['ID']}［{r['ステータス']}］（{meta}）", "", r["問題文"], ""]
            for i in range(1, 5):
                mark = " ✅" if i == ans else ""
                out.append(f"{i}. {r[f'選択肢{i}']}{mark}")
            out += ["", f"**正解：{ans}. {r[f'選択肢{ans}']}**", "", f"解説：{r['解説']}"]
            if r["出典URL"]:
                links = " ".join(f"<{u.strip()}>" for u in r["出典URL"].split("|") if u.strip())
                out += ["", f"出典：{links}"]
            if r["X正答率"]:
                out += ["", f"X正答率：{r['X正答率']}（{r['X投稿日']}）"]
    return "\n".join(out) + "\n"


def main():
    rows = load()
    errors, warnings = check(rows)
    for w in warnings:
        print("警告:", w)
    if errors:
        for e in errors:
            print("エラー:", e)
        sys.exit(1)
    OUT.write_text(render(rows), encoding="utf-8")
    print(f"{len(rows)}問をチェックし、{OUT.relative_to(ROOT)} を作成しました（警告{len(warnings)}件）")


if __name__ == "__main__":
    main()
