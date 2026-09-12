#!/usr/bin/env python3
"""デモ用ダミーデータ生成。lecturers.csv（30講師）と students.csv（300生徒の第1〜第4希望）を出力。
使い方: python3 make_dummy.py"""
import csv, random

random.seed(42)

LECTURES = [
    ("プログラミング入門", "ITエンジニア"), ("ゲームクリエイターの仕事", "ゲーム開発者"),
    ("YouTube動画のつくり方", "動画クリエイター"), ("パティシエ体験", "パティシエ"),
    ("看護師のリアル", "看護師"), ("消防士の一日", "消防士"), ("警察官の仕事", "警察官"),
    ("宇宙とロケット開発", "航空宇宙エンジニア"), ("獣医師と動物たち", "獣医師"),
    ("建築デザインの世界", "建築家"), ("マンガ家になるには", "マンガ家"),
    ("プロサッカー選手の話", "元プロサッカー選手"), ("弁護士のお仕事", "弁護士"),
    ("農業とスマート農業", "農業経営者"), ("美容師・ヘアメイク", "美容師"),
    ("新聞記者の取材現場", "新聞記者"), ("薬剤師と薬のはなし", "薬剤師"),
    ("保育士の仕事", "保育士"), ("鉄道運転士の仕事", "鉄道運転士"),
    ("パイロットの視点", "パイロット"), ("料理人の技", "和食料理人"),
    ("銀行と金融のしくみ", "銀行員"), ("翻訳・通訳の世界", "通訳者"),
    ("環境保護とSDGs", "NPO職員"), ("科学者の研究生活", "大学研究者"),
    ("ファッションデザイン", "ファッションデザイナー"), ("声優・アナウンサー", "アナウンサー"),
    ("大工とものづくり", "大工"), ("公務員の仕事", "市役所職員"), ("起業家の挑戦", "起業家"),
]
SURNAMES = "佐藤 鈴木 高橋 田中 伊藤 渡辺 山本 中村 小林 加藤 吉田 山田 佐々木 山口 松本 井上 木村 林 斎藤 清水 山崎 森 池田 橋本 阿部 石川 石井 前田 藤田 小川 岡田 後藤 長谷川 村上 近藤 石田 坂本 遠藤 青木 藤井".split()
GIVEN = "陽翔 蓮 悠真 湊 樹 大翔 蒼 颯太 結翔 陸 陽菜 凛 葵 結菜 咲良 芽依 紬 澪 莉子 心春 大和 翔 悠人 拓海 優斗 美咲 さくら 七海 愛莉 花音 健太 翼 太陽 光 拓真 千尋 遥 楓 杏 琴音".split()

def name(): return f"{random.choice(SURNAMES)} {random.choice(GIVEN)}"

# 講師: 前半/後半それぞれ定員。合計が各枠300以上になるまで引き直す
while True:
    lecturers = [(i + 1, name(), title, job, random.randint(6, 16), random.randint(6, 16))
                 for i, (title, job) in enumerate(LECTURES)]
    if sum(l[4] for l in lecturers) >= 300 and sum(l[5] for l in lecturers) >= 300:
        break

with open("lecturers.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["講師ID", "講師名", "授業名", "職業", "前半定員", "後半定員"])
    w.writerows(lecturers)

# 生徒: 人気に偏りを持たせる（Zipf風の重み）。第1〜第4希望は重複なし
ids = [l[0] for l in lecturers]
weights = [1 / (r + 1) ** 0.8 for r in random.sample(range(30), 30)]
students = []
for i in range(300):
    grade, cls = i // 100 + 1, (i % 100) // 34 + 1
    prefs = []
    while len(prefs) < 4:
        p = random.choices(ids, weights)[0]
        if p not in prefs:
            prefs.append(p)
    students.append([i + 1, name(), f"{grade}-{cls}", *prefs])

with open("students.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["生徒ID", "氏名", "クラス", "第1希望", "第2希望", "第3希望", "第4希望"])
    w.writerows(students)

# self-check
assert len(lecturers) == 30 and len(students) == 300
assert all(len(set(s[3:])) == 4 for s in students)
print("ok: lecturers.csv, students.csv")
