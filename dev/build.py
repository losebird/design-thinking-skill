#!/usr/bin/env python3
"""开发用：把 src/_base.css、src/_base.js 与各页面源码组装成 templates/ 下的单文件模板。
用法: python dev/build.py"""
import json, re, pathlib, sys
root = pathlib.Path(__file__).resolve().parent
ROOT = root.parent
src, out = root / "src", ROOT / "templates"
css, js = (src / "_base.css").read_text("utf-8"), (src / "_base.js").read_text("utf-8")
REG = json.loads((ROOT / "tools.json").read_text("utf-8"))
TOOLS, PHASES = REG["tools"], REG["phases"]
reg_js = json.dumps({"phases": PHASES, "tools": [{k: t[k] for k in ("phase", "name", "file", "tpl", "path", "check", "core", "desc", "when")} for t in TOOLS]}, ensure_ascii=False, separators=(",", ":"))
assert "/*DT_TOOLS*/null" in js, "_base.js 缺少 /*DT_TOOLS*/null 占位"
js = js.replace("/*DT_TOOLS*/null", reg_js.replace("</", "<\\/"), 1)

# 注册表自检：模板存在、文件名唯一、阶段合法
problems = []
names = {f.stem for f in src.glob("*.html") if not f.name.startswith("_")}
for t in TOOLS:
    if t["tpl"] not in names: problems.append(f"{t['file']}: 模板 {t['tpl']} 不存在")
    if t["phase"] not in {p["k"] for p in PHASES}: problems.append(f"{t['file']}: 未知阶段 {t['phase']}")
    if not t.get("check") or not t.get("path"): problems.append(f"{t['file']}: 缺少 check / path")
dup = {t["file"] for t in TOOLS if [x["file"] for x in TOOLS].count(t["file"]) > 1}
if dup: problems.append(f"文件名重复：{', '.join(sorted(dup))}")
orphan = names - {t["tpl"] for t in TOOLS} - {"overview", "dashboard"}
if orphan: problems.append(f"模板未登记到 tools.json：{', '.join(sorted(orphan))}")
if problems:
    sys.exit("tools.json 有问题：\n  " + "\n  ".join(problems))
SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 设计思维</title>
<style>
{css}
{pcss}
</style>
</head>
<body data-tpl="{name}">
<div class="wrap">
<header class="dt-head" id="dt-head"></header>
<main id="app"></main>
<div class="foot">设计思维 Skill · 修改会自动保存在本浏览器 · 点「复制给 AI」把结果带回对话</div>
</div>
<script id="dt-data" type="application/json">/*DT_DATA*/</script>
<script>
{js}
{pjs}
</script>
</body>
</html>
"""
out.mkdir(exist_ok=True)
for f in sorted(src.glob("*.html")):
    if f.name.startswith("_"):
        continue
    s = f.read_text("utf-8")
    title = re.search(r"<!--\s*title:\s*(.+?)\s*-->", s).group(1)
    pcss = "\n".join(re.findall(r"<style>(.*?)</style>", s, re.S))
    pjs = "\n".join(re.findall(r"<script>(.*?)</script>", s, re.S))
    html = SHELL.format(title=title, css=css, pcss=pcss.strip(), name=f.stem, js=js, pjs=pjs.strip())
    (out / f.name).write_text(html, "utf-8")
    print("built", f.name)

# 生成 references/tools-index.md 的工具表，并同步 SKILL.md / README 中的工具数
N = len(TOOLS)
PN = {"empathize": "共情", "define": "定义", "ideate": "构思", "prototype": "原型", "test": "测试", "reflect": "反思"}
rows = ["| 全程 | 项目仪表盘（入口） | dashboard / dashboard.html | 整个项目 | SKILL.md |",
        "| 全程 | 项目总览 + 工具速查 | overview / overview.html | 整个项目 | 本文件 |"]
rows += [f"| {PN[t['phase']]} | {t['name']} | {t['tpl']} / {t['file']} | {'、'.join('`' + p + '`' for p in t['path'])} | {t.get('method', '')} |" for t in TOOLS]
idx = ROOT / "references" / "tools-index.md"
s = idx.read_text("utf-8")
block = "<!-- tools:start（由 dev/build.py 根据 tools.json 生成，请勿手改） -->\n| 阶段 | 工具 | 模板 / 输出文件 | 数据路径 | 方法 |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n<!-- tools:end -->"
s2 = re.sub(r"<!-- tools:start.*?<!-- tools:end -->", lambda m: block, s, flags=re.S)
if s2 != s: idx.write_text(s2, "utf-8"); print("updated references/tools-index.md")
for f in ("SKILL.md", "README.md"):
    p = ROOT / f
    t = p.read_text("utf-8"); t2 = re.sub(r"\d+(?= ?个工具)", str(N), t)
    if t2 != t: p.write_text(t2, "utf-8"); print("updated", f, "→", N, "个工具")
print(f"tools.json: {N} 个工具")
