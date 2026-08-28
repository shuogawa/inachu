# 伊那中学校マインクエスト「システム開発の仕事と少しAIの話」

## 概要

中学生にシステム開発の仕事を伝える(google collabo)
またAI革命の影響も伝える

題材は **高速バスの予約システム**（伊那 ⇄ 新宿）。
生徒が実際に乗るバスの裏側を、MySQL のテーブルとして自分で作って動かす。

授業で配るノートブック: [`lesson.ipynb`](./lesson.ipynb)（27セル / 下の教材SQLを埋め込み済み）
Colab: ファイル > ノートブックをアップロード で開く → 生徒には「ドライブにコピーを保存」させる。

## まずは以下にページ案を作成する
想定: 中学生 / 50分 / Google Colab を各自の端末で開いて手を動かす。
1ページ = Colab の 1セクション(見出しセル + コードセル)。

### 1. こんにちは（3分）
- 自己紹介、今日やること3行。
- 「このページ自体がプログラムで動いてます」を最初の実行体験に。
- コード: `print("伊那中のみなさん、こんにちは！")` を全員1回実行。

### 2. 高速バスの予約、あれどうなってる？（7分）
- 目的: 「システム開発」を身近なものに翻訳する。
- 伊那 ⇄ 新宿のバスを予約する画面 → 裏では「誰がどの席を取ったか」を記録している。
- 質問から入る: 満席かどうか、どうやって分かる？ 同じ席が2人に売れたら？
- 画面 / サーバー / データベース の3つに分けて図解。今日触るのは一番奥の DB。

### 3. エンジニアの1日（7分）
- 目的: 仕事のイメージを具体化。
- 時間割形式で朝会〜設計〜コード〜レビュー〜リリース。
- 「1人で作ってない」= チームの役割(企画/デザイン/開発/テスト)。
- 給料・働き方・在宅などリアルな話を少し。

### 4. 予約システムのデータベースを作る（12分）★メイン
- 目的: CREATE → INSERT → SELECT を自分の手で通す。
- 下の「教材SQL」を上から実行。テーブルは4つだけ。
- 見せ場は3つ:
  1. 便 × 座席 16行を手打ちせず `INSERT ... SELECT` で作らせる
  2. `SELECT` で「窓側の空席」が一発で出る
  3. 同じ席を2人が予約しようとすると **DB がエラーを出して止める**
- 発展: 自分の名前で好きな席を予約 → 空席数が減るのを確認。

### 5. AIにコードを書かせる（10分）
- 目的: 今の開発現場の実態を見せる。
- 「このテーブルから○○を調べる SQL を書いて」を目の前でライブデモ。
- お題は生徒から募る(一番安い便、2人並びで空いてる席、など)。
- 「AIが書く。でも、何を作るか決めて、合ってるか判断するのは人間」。

### 6. AIで仕事はどうなる？（8分）
- 目的: 不安に正面から答える。
- 消える作業 / 残る仕事 / 新しく生まれた仕事を3列で。
- 自分の仕事がこの2〜3年でどう変わったかの実体験。
- 結論: 道具が変わるだけ、決める力と作りたい気持ちは残る。

### 7. 今からできること・質問（5分）
- 目的: 持ち帰るものを1つ渡す。
- Colab は家でも無料で使える(このノートブックのURLを配る)。
- 質問タイム。答えを準備: 数学は必要? 大学は? 英語は? ゲームは作れる?

### 予備ページ（時間が余ったら）
- 予約をキャンセルする UPDATE / 別の車両を増やす。

---

## 教材SQL: 高速バス予約システム

### テーブルの役割（生徒への説明はこの4行だけ）

| テーブル | なにが入っているか |
|---|---|
| `car` | バスの車両。「伊那号 1号車」 |
| `car_chairs` | その車両のイス。1A, 1B ... 動かない情報 |
| `car_plan` | 運行の予定。9/5 8:00 伊那→新宿、を1行 |
| `car_plan_chairs` | **便ごとのイス。ここに予約が入る** |

なぜ `car_chairs` と `car_plan_chairs` を分けるか →
イスは毎日同じ、でも「誰が座るか」は便ごとに違う。ここが設計の話。

### Colab で MySQL を動かす（最初のセル / 1〜2分かかる）

```python
!apt-get -qq update && apt-get -qq install -y mysql-server > /dev/null
!service mysql start
!mysql -u root -e "CREATE DATABASE IF NOT EXISTS bus"
```

以降のセルは `%%writefile` で SQL を書き、`!mysql -u root --table bus < ファイル名` で実行。
（`--table` を付けると表の枠線付きで結果が出る）

### 1) CREATE TABLE

```sql
DROP TABLE IF EXISTS car_plan_chairs, car_plan, car_chairs, car;

-- 1) バスの車両
CREATE TABLE car (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL COMMENT '車両の呼び名'
);

-- 2) その車両のイス（物理的な座席）
CREATE TABLE car_chairs (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  car_id      INT         NOT NULL,
  seat_no     VARCHAR(5)  NOT NULL COMMENT '1A, 1B ...',
  window_side BOOLEAN     NOT NULL COMMENT '窓側なら true',
  UNIQUE (car_id, seat_no),
  FOREIGN KEY (car_id) REFERENCES car(id)
);

-- 3) 運行の予定（いつ・どこからどこへ・どの車両で）
CREATE TABLE car_plan (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  car_id       INT         NOT NULL,
  departure_at DATETIME    NOT NULL,
  origin       VARCHAR(50) NOT NULL,
  destination  VARCHAR(50) NOT NULL,
  price        INT         NOT NULL,
  FOREIGN KEY (car_id) REFERENCES car(id)
);

-- 4) 便ごとのイス = 予約が入る場所
CREATE TABLE car_plan_chairs (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  car_plan_id    INT         NOT NULL,
  car_chair_id   INT         NOT NULL,
  passenger_name VARCHAR(50) DEFAULT NULL COMMENT 'NULL なら空席',
  reserved_at    DATETIME    DEFAULT NULL,
  UNIQUE (car_plan_id, car_chair_id),   -- 同じ便の同じ席は1行だけ = 二重予約を防ぐ
  FOREIGN KEY (car_plan_id)  REFERENCES car_plan(id),
  FOREIGN KEY (car_chair_id) REFERENCES car_chairs(id)
);
```

### 2) INSERT

```sql
INSERT INTO car (name) VALUES ('伊那号 1号車'), ('伊那号 2号車');

INSERT INTO car_chairs (car_id, seat_no, window_side) VALUES
 (1,'1A',true),(1,'1B',false),(1,'1C',false),(1,'1D',true),
 (1,'2A',true),(1,'2B',false),(1,'2C',false),(1,'2D',true);

INSERT INTO car_plan (car_id, departure_at, origin, destination, price) VALUES
 (1,'2026-09-05 08:00:00','伊那','新宿',3800),
 (1,'2026-09-05 14:00:00','新宿','伊那',3800);

-- 便 × イス を手打ちしない（8席 × 2便 = 16行を SQL に作らせる）
INSERT INTO car_plan_chairs (car_plan_id, car_chair_id)
SELECT p.id, c.id FROM car_plan p JOIN car_chairs c ON c.car_id = p.car_id;

-- 予約が入る
UPDATE car_plan_chairs SET passenger_name='小川', reserved_at=NOW()
 WHERE car_plan_id=1 AND car_chair_id=(SELECT id FROM car_chairs WHERE car_id=1 AND seat_no='1A');
UPDATE car_plan_chairs SET passenger_name='田中', reserved_at=NOW()
 WHERE car_plan_id=1 AND car_chair_id=(SELECT id FROM car_chairs WHERE car_id=1 AND seat_no='2D');
```

### 3) SELECT

```sql
-- 便の一覧
SELECT p.id, c.name, p.departure_at, p.origin, p.destination, p.price
  FROM car_plan p JOIN car c ON c.id = p.car_id ORDER BY p.departure_at;

-- 1便目の座席表（空席 / 予約済み）
SELECT ch.seat_no, IF(ch.window_side,'窓側','通路側') AS `席`,
       IFNULL(pc.passenger_name,'空席') AS `状況`
  FROM car_plan_chairs pc JOIN car_chairs ch ON ch.id = pc.car_chair_id
 WHERE pc.car_plan_id = 1 ORDER BY ch.seat_no;

-- 便ごとの空席数
SELECT p.departure_at, p.origin, p.destination,
       COUNT(*) AS `全席`, SUM(pc.passenger_name IS NULL) AS `空席`
  FROM car_plan p JOIN car_plan_chairs pc ON pc.car_plan_id = p.id
 GROUP BY p.id ORDER BY p.departure_at;

-- 窓側の空席だけ探す
SELECT p.departure_at, ch.seat_no
  FROM car_plan_chairs pc
  JOIN car_chairs ch ON ch.id = pc.car_chair_id
  JOIN car_plan   p  ON p.id  = pc.car_plan_id
 WHERE pc.passenger_name IS NULL AND ch.window_side = true
 ORDER BY p.departure_at, ch.seat_no;
```

### 4) わざとエラーを出す（ここが一番ウケる）

```sql
-- 1便目の1A席を、もう一度作ろうとする
INSERT INTO car_plan_chairs (car_plan_id, car_chair_id) VALUES (1, 1);
-- => ERROR 1062 Duplicate entry '1-1' for key 'car_plan_chairs.car_plan_id'
```

「人間が気をつける」ではなく「間違えられない形にしておく」のが設計の仕事、という話に繋げる。

### 実行結果（手元の MySQL 8 で確認済み）

```
+----+-------------------+---------------------+--------+-------------+-------+
| id | name              | departure_at        | origin | destination | price |
+----+-------------------+---------------------+--------+-------------+-------+
|  1 | 伊那号 1号車      | 2026-09-05 08:00:00 | 伊那   | 新宿        |  3800 |
|  2 | 伊那号 1号車      | 2026-09-05 14:00:00 | 新宿   | 伊那        |  3800 |
+----+-------------------+---------------------+--------+-------------+-------+

+---------+----------+--------+        +---------------------+--------+--------+
| seat_no | 席       | 状況   |        | departure_at        | 全席   | 空席   |
+---------+----------+--------+        +---------------------+--------+--------+
| 1A      | 窓側     | 小川   |        | 2026-09-05 08:00:00 |      8 |      6 |
| 1B      | 通路側   | 空席   |        | 2026-09-05 14:00:00 |      8 |      8 |
| ...     |          |        |        +---------------------+--------+--------+
| 2D      | 窓側     | 田中   |
+---------+----------+--------+
```
