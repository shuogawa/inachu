#!/usr/bin/env python3
"""lesson.ipynb 自身のセットアップと全SQLを手元のMySQLで通す。
使い方: docker compose up -d && python3 check.py"""
import contextlib, io, json, re

code = ["".join(c["source"]) for c in json.load(open("lesson.ipynb"))["cells"]
        if c["cell_type"] == "code"]

# ノートブックのセットアップセルをそのまま実行（Colab専用の ! 行だけ除く）
setup = next(c for c in code if "def sql(" in c)
ns = {}
exec("\n".join(l for l in setup.splitlines() if not l.lstrip().startswith("!")), ns)

def run(q):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ns["sql"](q)
    return buf.getvalue()

fails = []
for i, q in enumerate(m for c in code for m in re.findall(r'sql\("""(.*?)"""\)', c, re.S)):
    out = run(q)
    err = "ERROR" in out
    want_err = "VALUES (1, 1)" in q          # 7章: わざと失敗させるセル
    if err == want_err:
        print(f"[{i}] {'期待どおり失敗' if want_err else 'OK'}")
    else:
        print(f"[{i}] NG")
        fails.append((i, q.strip().splitlines()[0][:50], out.strip()[:200]))

assert "16" in run("SELECT COUNT(*) FROM car_plan_chairs;"), "座席が16行になっていない"
assert not fails, fails
print("全セルOK")
