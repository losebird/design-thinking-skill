#!/usr/bin/env python3
"""把设计思维项目 JSON 渲染成可交互的 HTML 页面（仅需 Python 3 标准库）。

用法:
  python3 render.py <模板名或路径> <数据.json> <输出.html> [--target boards.retro]
  python3 render.py --all <数据.json> <输出目录>      # 按数据内容批量生成全部页面
  python3 render.py --list                           # 列出模板与预设
  python3 render.py --preset boards.retro            # 打印某个预设的 JSON

说明:
  * 模板名如 persona / empathy-map / board，对应 templates/<名>.html。
  * board / table / radial 是通用模板，用 --target 指定数据路径，例如 boards.retro、tables.experiments。
    若 presets/ 里有同名预设（如 boards.retro），会自动补全列定义、说明等，数据中的字段优先。
  * 不能运行 Python 时，可手动把模板中的 /*DT_DATA*/ 替换为 JSON（其中 "</" 写成 "<\\/"）。
"""
import copy, datetime, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate import check

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL, PRE = ROOT / "templates", ROOT / "presets"
GENERIC = {"boards": "board", "tables": "table", "radials": "radial"}
REG = json.loads((ROOT / "tools.json").read_text("utf-8"))


def has(o):
    """与页面 DT.has 一致：空字符串 / 空数组 / 只有 id 的对象 / false / 0 视为无内容。"""
    if o is None or o is False: return False
    if isinstance(o, list): return len(o) > 0
    if isinstance(o, dict): return any(k != "id" and has(v) for k, v in o.items())
    if isinstance(o, (int, float)): return o != 0
    return str(o).strip() != ""


def at(d, path):
    for k in path.split("."):
        if not isinstance(d, dict): return None
        d = d.get(k)
    return d


def has_data(tool, d):
    return any(has(at(d, p)) for p in tool["check"])


# (输出文件, 模板, 判断数据是否存在)——专用模板来自 tools.json；通用模板（board/table/radial）按数据中的键生成
PAGES = [("overview.html", "overview", lambda d: True)] + [
    (t["file"], t["tpl"], (lambda t: lambda d: has_data(t, d))(t)) for t in REG["tools"] if t["tpl"] not in GENERIC.values()
] + [("dashboard.html", "dashboard", lambda d: True)]


def load_presets():
    out = {}
    for group in GENERIC:
        f = PRE / (group + ".json")
        out[group] = json.loads(f.read_text("utf-8")) if f.exists() else {}
    return out


def merge(base, over):
    if isinstance(base, dict) and isinstance(over, dict):
        r = dict(base)
        for k, v in over.items():
            r[k] = merge(base[k], v) if k in base else v
        return r
    return copy.deepcopy(over)


MVP_ALIAS = {"hypo": ["hypothesis"]}


def normalize(d):
    """兼容旧写法，让所有页面读到同一结构：
    tables.*.questions / items → rows；boards.* 中与列同名的画布字段（如 mvp 的 hypothesis）→ cards。"""
    for t in (d.get("tables") or {}).values():
        if isinstance(t, dict) and not t.get("rows"):
            for alt in ("questions", "items"):
                if isinstance(t.get(alt), list) and t[alt]:
                    t["rows"] = t.pop(alt); break
        for i, r in enumerate((t or {}).get("rows") or []):
            if isinstance(r, dict) and not r.get("id"):
                r["id"] = f"r{i + 1}"
    for b in (d.get("boards") or {}).values():
        if not isinstance(b, dict) or not b.get("columns"):
            continue
        cards = b.setdefault("cards", {})
        for c in b["columns"]:
            k = c["key"]
            if cards.get(k):
                continue
            for f in [k] + MVP_ALIAS.get(k, []):
                v = b.get(f)
                if v is None or isinstance(v, dict):
                    continue
                items = [x if isinstance(x, str) else (x or {}).get("text", "") for x in (v if isinstance(v, list) else [v])]
                cards[k] = [{"id": f"{k[:2]}{i + 1}", "text": t} for i, t in enumerate(items) if t]
                b.pop(f); break
    return d


def with_presets(data):
    """为 boards/tables/radials 中与预设同名的项补全默认结构，并统一旧写法。"""
    pre, d = load_presets(), copy.deepcopy(data)
    for group in GENERIC:
        for key, val in (d.get(group) or {}).items():
            if key in pre[group] and isinstance(val, dict):
                d[group][key] = merge(pre[group][key], val)
    return normalize(d)


def tpl_path(name):
    p = pathlib.Path(name)
    if p.suffix == ".html" and p.exists():
        return p
    stem = name[:-5] if name.endswith(".html") else name
    p = TPL / (pathlib.Path(stem).name + ".html")
    if not p.exists():
        sys.exit(f"找不到模板: {name}（可用: {', '.join(sorted(x.stem for x in TPL.glob('*.html')))}）")
    return p


def render(tpl, data, out, target=None, rev=None, pages=None):
    data = with_presets(data)
    if pages is not None:
        data["_pages"] = pages  # 已生成的页面，仪表盘 / 总览据此显示“打开”链接
    data["_rev"] = rev or datetime.datetime.now().isoformat(timespec="seconds")  # 渲染时间，页面据此判断数据新旧
    if target:
        data["_target"] = target
        group, _, key = target.partition(".")
        if group in GENERIC and key:
            data.setdefault(group, {}).setdefault(key, copy.deepcopy(load_presets()[group].get(key, {})))
    html = tpl_path(tpl).read_text("utf-8")
    if "/*DT_DATA*/" not in html:
        sys.exit("模板中没有 /*DT_DATA*/ 占位符")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html.replace("/*DT_DATA*/", payload, 1), "utf-8")
    return out


def render_all(data, outdir):
    outdir = pathlib.Path(outdir)
    rev = datetime.datetime.now().isoformat(timespec="seconds")
    jobs = [(tpl, fname, None) for fname, tpl, ok in PAGES if ok(data)]
    for group, tpl in GENERIC.items():
        for key in (data.get(group) or {}):
            jobs.append((tpl, f"{tpl}-{key}.html", f"{group}.{key}"))
    pages = [f for _, f, _ in jobs]
    return [render(tpl, data, outdir / f, target, rev, pages) for tpl, f, target in jobs]


def report(data):
    E, W = check(data)
    for x in E: print("❌", x)
    for x in W: print("⚠️ ", x)
    if E or W:
        print(f"数据检查：{len(E)} 个错误，{len(W)} 个提醒（详见 scripts/validate.py）")


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    if a[0] == "--list":
        print("模板:", ", ".join(sorted(x.stem for x in TPL.glob("*.html"))))
        for g, items in load_presets().items():
            print(f"{g}:", ", ".join(f"{k}（{v.get('title', '')}）" for k, v in items.items()))
        return
    if a[0] == "--preset":
        g, _, k = a[1].partition(".")
        print(json.dumps(load_presets()[g][k], ensure_ascii=False, indent=1)); return
    if a[0] == "--all":
        data = json.loads(pathlib.Path(a[1]).read_text("utf-8"))
        report(data)
        for p in render_all(data, a[2]):
            print("已生成", p)
        return
    target = None
    if "--target" in a:
        i = a.index("--target"); target = a[i + 1]; a = a[:i] + a[i + 2:]
    if len(a) != 3:
        sys.exit(__doc__)
    data = json.loads(pathlib.Path(a[1]).read_text("utf-8"))
    report(data)
    print("已生成", render(a[0], data, a[2], target))


if __name__ == "__main__":
    main(sys.argv[1:])
