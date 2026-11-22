#!/usr/bin/env python3
"""开发用：把 src/_base.css、src/_base.js 与各页面源码组装成 templates/ 下的单文件模板。
用法: python dev/build.py"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent
src, out = root / "src", root.parent / "templates"
css, js = (src / "_base.css").read_text("utf-8"), (src / "_base.js").read_text("utf-8")
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
