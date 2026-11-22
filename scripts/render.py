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
PAGES = [  # (输出文件, 模板, 判断数据是否存在)
    ("overview.html", "overview", lambda d: True),
    ("persona.html", "persona", lambda d: bool(d.get("personas") or d.get("persona"))),
    ("empathy-map.html", "empathy-map", lambda d: bool(d.get("empathyMap"))),
    ("journey.html", "journey", lambda d: bool((d.get("journey") or {}).get("stages"))),
    ("hook.html", "hook", lambda d: bool(d.get("hook"))),
    ("pov.html", "pov", lambda d: bool(d.get("define"))),
    ("scamper.html", "scamper", lambda d: bool((d.get("ideate") or {}).get("scamper"))),
    ("matrix.html", "matrix", lambda d: bool((d.get("ideate") or {}).get("matrix"))),
    ("box.html", "box", lambda d: bool(d.get("prototype"))),
    ("storyboard.html", "storyboard", lambda d: bool((d.get("storyboard") or {}).get("frames"))),
    ("value-canvas.html", "value-canvas", lambda d: bool(d.get("valueCanvas"))),
    ("ab-test.html", "ab-test", lambda d: bool((d.get("test") or {}).get("ab"))),
    ("research-plan.html", "research-plan", lambda d: bool(d.get("researchPlan"))),
    ("dashboard.html", "dashboard", lambda d: True),
]


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


def with_presets(data):
    """为 boards/tables/radials 中与预设同名的项补全默认结构。"""
    pre, d = load_presets(), copy.deepcopy(data)
    for group in GENERIC:
        for key, val in (d.get(group) or {}).items():
            if key in pre[group] and isinstance(val, dict):
                d[group][key] = merge(pre[group][key], val)
    return d


def tpl_path(name):
    p = pathlib.Path(name)
    if p.suffix == ".html" and p.exists():
        return p
    stem = name[:-5] if name.endswith(".html") else name
    p = TPL / (pathlib.Path(stem).name + ".html")
    if not p.exists():
        sys.exit(f"找不到模板: {name}（可用: {', '.join(sorted(x.stem for x in TPL.glob('*.html')))}）")
    return p


def render(tpl, data, out, target=None, rev=None):
    data = with_presets(data)
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
    outdir, made = pathlib.Path(outdir), []
    rev = datetime.datetime.now().isoformat(timespec="seconds")
    for fname, tpl, ok in PAGES:
        if ok(data):
            made.append(render(tpl, data, outdir / fname, rev=rev))
    for group, tpl in GENERIC.items():
        for key in (data.get(group) or {}):
            made.append(render(tpl, data, outdir / f"{tpl}-{key}.html", f"{group}.{key}", rev))
    return made


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
