#!/usr/bin/env python3
"""ipynb から実行結果を取り除く。git の clean フィルタとして使う（stdin -> stdout）。"""
import json, sys

nb = json.load(sys.stdin)
for c in nb["cells"]:
    if c["cell_type"] == "code":
        c["outputs"], c["execution_count"] = [], None
nb.get("metadata", {}).pop("widgets", None)   # ipywidgets の状態も残さない
json.dump(nb, sys.stdout, ensure_ascii=False, indent=1)
sys.stdout.write("\n")
