#!/usr/bin/env python3
"""检查设计思维项目 JSON 的结构与质量（仅需 Python 3 标准库）。

用法: python3 validate.py project.json
输出 ❌ 错误（会导致页面异常，必须修正）与 ⚠️ 提醒（质量问题，建议修正）。
有错误时退出码为 1。render.py 渲染前也会自动运行本检查。
"""
import json, re, sys, pathlib

SOL_TERMS = ["App","APP","app","应用","小程序","平台","系统","功能","按钮","界面","页面","网站","设备","机器","柜","台灯","灯具","推送","通知","算法","插件","软件","硬件","二维码","优惠券","会员卡","机器人","AI","传感器","屏幕"]
SOL = re.compile(r"(" + "|".join(re.escape(t) for t in SOL_TERMS) + r")")


def sol_check(text, domain_terms=()):
    """检查文本是否含方案词；domain_terms 为白名单（meta.domainTerms），命中则跳过。
    逐词判断：只有所有命中词都在白名单里时才返回 None，否则返回第一个非白名单方案词。
    """
    for m in SOL.finditer(text):
        if m.group(1) not in (domain_terms or []):
            return m.group(1)
    return None
EV = {"quote", "observed", "inferred", "assumed"}
EM_ZONES = ["sees", "hears", "says", "does", "thinks", "feels", "pains", "gains"]


def check(d):
    E, W = [], []
    err, warn = E.append, W.append
    if not isinstance(d, dict):
        return ["顶层必须是 JSON 对象"], []

    # domainTerms 白名单（meta.domainTerms 中的词不触发 SOL 方案词告警）
    domain_terms = (d.get("meta") or {}).get("domainTerms") or []
    sol = lambda text: sol_check(text, domain_terms)

    # 顶层结构检查
    reg = json.loads((pathlib.Path(__file__).resolve().parent.parent / "tools.json").read_text("utf-8"))
    KNOWN_TOP = {p.split(".")[0] for t in reg["tools"] for p in t["path"] + t["check"]} | {
        'meta', 'project', 'name', '_target', '_rev', '_pages'}
    SHOULD_NEST = {'pov':'define.pov','scamper':'ideate.scamper','matrix':'ideate.matrix',
                   'box':'prototype.box','plan':'prototype.plan','ab':'test.ab'}
    for k in d:
        if k in SHOULD_NEST:
            err(f"字段 '{k}' 写在顶层，应放在 {SHOULD_NEST[k]} 下（agent 常见错误）")
        elif k not in KNOWN_TOP:
            warn(f"未知顶层字段 '{k}'，可能路径错误")
    meta = d.get("meta") or {}
    if not meta.get("project"):
        warn("meta.project 为空：页面标题和浏览器保存键会用 default")
    gb = meta.get("generatedBy", "ai")
    if gb not in ("ai", "mixed", "human"):
        err(f"meta.generatedBy 只能是 ai / mixed / human，当前为 {gb!r}")

    # ── 阶段入场条件检查 ──────────────────────────────────────────────
    # 顺序：empathize(0) → define(1) → ideate(2) → prototype(3) → test(4) → reflect(5)
    # 若 meta.phase 声明已进入某阶段，检查前序必备数据是否存在。
    PHASE_ORDER = ["empathize", "define", "ideate", "prototype", "test", "reflect"]
    phase = meta.get("phase", "empathize")
    if phase not in PHASE_ORDER:
        warn(f"meta.phase 值 {phase!r} 不合法，应为 {PHASE_ORDER}")
    else:
        pi = PHASE_ORDER.index(phase)

        def _nonempty(path):
            """检查 path（点分）对应的值是否非空（非 None / 非空列表 / 非空对象 / 非空字符串）。"""
            o = d
            for k in path.split("."):
                if not isinstance(o, dict):
                    return False
                o = o.get(k)
            if o is None:
                return False
            if isinstance(o, (list, dict)):
                return bool(o)
            return str(o).strip() not in ("", "false", "False")

        # 进入 define 阶段：需要至少 1 个画像 + 移情图有内容
        if pi >= 1:
            if not _nonempty("personas"):
                warn("meta.phase 已是 define 或更后阶段，但 personas 为空；进入定义阶段前需至少完成 1 个用户画像")
            if not _nonempty("empathyMap"):
                warn("meta.phase 已是 define 或更后阶段，但 empathyMap 为空；进入定义阶段前需完成移情图")

        # 进入 ideate 阶段：需要 JTBD + PoV + 至少 1 条 HMW
        if pi >= 2:
            if not _nonempty("define.jtbd"):
                warn("meta.phase 已是 ideate 或更后阶段，但 define.jtbd 为空；进入构思阶段前需完成 JTBD 语句")
            if not _nonempty("define.pov"):
                warn("meta.phase 已是 ideate 或更后阶段，但 define.pov 为空；进入构思阶段前需完成 PoV 句子")
            if not _nonempty("define.hmw"):
                warn("meta.phase 已是 ideate 或更后阶段，但 define.hmw 为空；进入构思阶段前需至少 1 条 HMW 问题")

        # 进入 prototype 阶段：丘吉尔矩阵有 selected 点子 + 至少用过一种发散工具
        if pi >= 3:
            mx_raw = (d.get("ideate") or {}).get("matrix") or {}
            matrix_items = mx_raw.get("items", []) if isinstance(mx_raw, dict) else mx_raw
            if not any(isinstance(x, dict) and x.get("selected") for x in matrix_items):
                warn("meta.phase 已是 prototype 或更后阶段，但 ideate.matrix 中没有 selected:true 的点子；进入原型阶段前需在丘吉尔矩阵中选定至少 1 个方向")
            has_diverge = (_nonempty("boards.brainstorm") or _nonempty("boards.crazy8")
                           or _nonempty("ideate.scamper"))
            if not has_diverge:
                warn("meta.phase 已是 prototype 或更后阶段，但没有使用任何发散工具（头脑风暴 / Crazy 8s / SCAMPER 均为空）；进入原型阶段前至少用一种发散工具产生点子")

        # 进入 test 阶段：需要盒子原则 + 原型规划
        if pi >= 4:
            if not _nonempty("prototype.box"):
                warn("meta.phase 已是 test 或更后阶段，但 prototype.box 为空；进入测试阶段前需完成盒子原则")
            if not _nonempty("prototype.plan"):
                warn("meta.phase 已是 test 或更后阶段，但 prototype.plan 为空；进入测试阶段前需完成原型规划")

        # 进入 reflect 阶段：至少完成一份测试计划
        if pi >= 5:
            if not _nonempty("tables.testplan"):
                warn("meta.phase 已是 reflect，但 tables.testplan 为空；进入反思阶段前需至少完成一份测试计划")

    def ids(path, arr):
        if not isinstance(arr, list):
            err(f"{path} 应为数组"); return
        seen = set()
        for i, x in enumerate(arr):
            if not isinstance(x, dict):
                continue
            if not x.get("id"):
                err(f"{path}[{i}] 缺少 id")
            elif x["id"] in seen:
                err(f"{path} 中 id 重复：{x['id']}")
            seen.add(x.get("id"))

    # 画像
    ps = d.get("personas") or []
    ids("personas", ps)
    for i, p in enumerate(ps):
        miss = [k for k in ("name", "snapshot", "tags", "jobs", "pains", "behaviors", "motivation", "quote") if not p.get(k)]
        if miss:
            warn(f"personas[{i}]（{p.get('name', '')}）缺少画布要素：{', '.join(miss)}")
        j = p.get("jobs") or {}
        if j and not all(j.get(k) for k in ("functional", "emotional", "social")):
            warn(f"personas[{i}].jobs 应区分功能 / 情感 / 社交三类需求")
        for x in p.get("pains") or []:
            if isinstance(x, dict) and sol(x.get("text", "")):
                warn(f"personas[{i}] 痛点含方案词：{x.get('text')}")

    # 故事板
    pids = {p.get("id") for p in ps if isinstance(p, dict)}
    sb = d.get("storyboard")
    if sb:
        fr = sb.get("frames") or []
        ids("storyboard.frames", fr)
        if sb.get("personaId") and sb["personaId"] not in pids:
            err(f"storyboard.personaId 不存在：{sb['personaId']}")
        if fr and not 3 <= len(fr) <= 8:
            warn(f"storyboard 有 {len(fr)} 格，建议 4–8 格（起因→经过→转折→结果）")
        for i, f in enumerate(fr):
            if not f.get("action"):
                warn(f"storyboard.frames[{i}] 缺少 action（这一格发生了什么）")
            e = f.get("emotion", 0)
            if not isinstance(e, (int, float)) or not -2 <= e <= 2:
                err(f"storyboard.frames[{i}].emotion 应为 -2 到 2 的数字")
            if f.get("hook") not in (None, "", "trigger", "action", "reward", "investment"):
                err(f"storyboard.frames[{i}].hook 只能是 trigger/action/reward/investment 或空")
        if not sb.get("toVerify"):
            warn("storyboard.toVerify 为空：故事里哪些情节是推测的？")

    # 价值主张画布
    vc = d.get("valueCanvas")
    if vc:
        if vc.get("personaId") and vc["personaId"] not in pids:
            err(f"valueCanvas.personaId 不存在：{vc['personaId']}")
        for k in ("jobs", "pains", "gains", "products", "relievers", "creators"):
            ids(f"valueCanvas.{k}", vc.get(k) or [])
            if not vc.get(k):
                warn(f"valueCanvas.{k} 为空")
        pain_ids = {x.get("id") for x in vc.get("pains") or []}
        gain_ids = {x.get("id") for x in vc.get("gains") or []}
        for k, ok, nm in (("relievers", pain_ids, "痛点"), ("creators", gain_ids, "收益")):
            for x in vc.get(k) or []:
                bad = [t for t in x.get("targets") or [] if t not in ok]
                if bad:
                    err(f"valueCanvas.{k}（{x.get('text', '')}）关联了不存在的{nm}：{', '.join(bad)}")
                if not x.get("targets"):
                    warn(f"valueCanvas.{k}（{x.get('text', '')}）没有对应任何{nm}，可能是“自嗨功能”")
        for x in (vc.get("pains") or []) + (vc.get("jobs") or []) + (vc.get("gains") or []):
            if sol(x.get("text", "")):
                warn(f"valueCanvas 顾客侧含方案词（顾客档案应描述需求而非产品）：{x.get('text')}")
        for x in vc.get("jobs") or []:
            if x.get("type") not in ("functional", "emotional", "social"):
                err(f"valueCanvas.jobs（{x.get('text', '')}）type 应为 functional/emotional/social")
        if not vc.get("toVerify"):
            warn("valueCanvas.toVerify 为空")

    # 移情图
    em = d.get("empathyMap")
    if em:
        all_ids = {}
        for z in EM_ZONES:
            arr = em.get(z) or []
            ids(f"empathyMap.{z}", arr)
            for x in arr:
                if not isinstance(x, dict):
                    err(f"empathyMap.{z} 的条目应为对象"); continue
                all_ids[x.get("id")] = z
                ev = x.get("evidence", "assumed")
                if ev not in EV:
                    err(f"empathyMap.{z} 中 {x.get('id')} 的 evidence 无效：{ev}")
                if gb == "ai" and ev in ("quote", "observed"):
                    warn(f"empathyMap.{z} 中 {x.get('id')} 标为{'原话' if ev == 'quote' else '观察'}，但 generatedBy=ai：AI 不能编造原话/观察，请改为 inferred/assumed，或把 generatedBy 改为 mixed/human")
        for z in ("says", "does", "thinks", "feels"):
            n = len(em.get(z) or [])
            if n < 2:
                warn(f"empathyMap.{z} 只有 {n} 条，建议 2–4 条")
        cs = em.get("contradictions") or []
        if len(cs) < 2:
            warn("empathyMap.contradictions 少于 2 条：洞察来自“说 vs 做 vs 想”的矛盾")
        for c in cs:
            for k in ("a", "b"):
                if c.get(k) not in all_ids:
                    err(f"empathyMap.contradictions 引用了不存在的卡片 id：{c.get(k)}")
            if not c.get("insight"):
                warn(f"矛盾 {c.get('a')} vs {c.get('b')} 缺少 insight")
        ci = em.get("coreInsight", "")
        if not ci:
            warn("empathyMap.coreInsight 为空")
        if not em.get("toVerify"):
            warn("empathyMap.toVerify 为空：请给出 2–4 条真人验证动作")
        if em.get("personaId") and ps and em["personaId"] not in {p.get("id") for p in ps}:
            err(f"empathyMap.personaId={em['personaId']} 在 personas 中不存在")

    # 旅程
    jn = d.get("journey")
    if jn:
        ids("journey.stages", jn.get("stages") or [])
        for s in jn.get("stages") or []:
            e = s.get("emotion", 0)
            if not isinstance(e, (int, float)) or not -2 <= e <= 2:
                err(f"journey 阶段「{s.get('name')}」emotion 应为 -2..2 的数字")
        if not any(s.get("opportunities") for s in jn.get("stages") or []):
            warn("journey 没有任何机会点 opportunities")

    # Hook
    hk = d.get("hook")
    if hk:
        et = hk.get("ethics") or {}
        if not et.get("improves") or not et.get("selfUse"):
            warn("hook.ethics 未填写：必须回答“是否改善用户生活”“自己是否会长期使用”")
        elif et.get("improves") == "no" and et.get("selfUse") == "no":
            warn("hook 伦理检查落在“操纵者”象限：请重新设计或明确告知用户风险")

    # 定义
    df = d.get("define")
    if df:
        ids("define.insights", df.get("insights") or [])
        ids("define.hmw", df.get("hmw") or [])
        pov = df.get("pov") or {}
        if pov.get("format") not in (None, "standard", "story", "storyPain", "hmw"):
            err(f"define.pov.format 无效：{pov.get('format')}")
        if sol(pov.get("need", "")):
            warn(f"PoV 需求含方案词（{sol(pov['need'])}）：方案不是需求，请改写为用户要完成的任务")
        if pov.get("insight") and len(pov["insight"]) < 12:
            warn("PoV 洞察过短，可能是“正确的废话”，请解释“为什么”")
        if not df.get("hmw"):
            warn("define.hmw 为空：建议导出 3–5 条 HMW")

    # 构思
    ide = d.get("ideate") or {}
    sc = ide.get("scamper")
    if sc:
        for k in "SCAMPER":
            ids(f"ideate.scamper.{k}", sc.get(k) or [])
    mx = ide.get("matrix")
    if mx and isinstance(mx, list):
        warn("ideate.matrix 应为对象（含 mode 和 items），当前是数组（旧格式），请按新结构迁移")
        mx = None
    if mx:
        if mx.get("mode") not in (None, "value", "urgency"):
            err(f"ideate.matrix.mode 只能是 value / urgency")
        ids("ideate.matrix.items", mx.get("items") or [])
        for it in mx.get("items") or []:
            for k in ("x", "y"):
                v = it.get(k)
                if not isinstance(v, (int, float)) or not 1 <= v <= 5:
                    err(f"矩阵项「{it.get('text')}」的 {k} 应为 1–5 的数字")
            if not it.get("note"):
                warn(f"矩阵项「{it.get('text')}」缺少 note（评分依据 / 关键假设）")

    # 原型
    pr = d.get("prototype")
    if pr:
        b = pr.get("box") or {}
        miss = [k for k in ("name", "slogan", "benefits", "features", "who", "why") if not b.get(k)]
        if miss:
            warn(f"prototype.box 缺少：{', '.join(miss)}")
        pl = pr.get("plan") or {}
        if pl.get("fidelity") not in (None, 0, 1, 2):
            err("prototype.plan.fidelity 只能是 0 / 1 / 2")
        if not pl.get("learn"):
            warn("prototype.plan.learn 为空：原型要写清“这次要学到什么”")

    # 测试
    ab = (d.get("test") or {}).get("ab")
    if ab:
        for k in ("a", "b"):
            g = ab.get(k) or {}
            n, c = g.get("n", 0), g.get("conv", 0)
            if not isinstance(n, int) or not isinstance(c, int) or n < 0 or c < 0:
                err(f"test.ab.{k} 的 n / conv 应为非负整数")
            elif c > n:
                err(f"test.ab.{k} 转化数 {c} 大于样本量 {n}")
        if not ab.get("hypothesis"):
            warn("test.ab.hypothesis 为空")
        if gb == "ai" and (ab.get("a") or {}).get("n") and "示例" not in json.dumps(ab, ensure_ascii=False):
            warn("A/B 数据在 generatedBy=ai 下出现：如果是示例数字，请在 name 或 desc 中注明“示例数据”")

    # 桌面研究（二手研究）
    dr = d.get("deskResearch")
    if dr is not None:
        if not isinstance(dr, dict):
            err("deskResearch 应为对象")
        else:
            check_desk(dr, err, warn, domain_terms)

    # 研究计划
    rp_data = d.get("researchPlan")
    if rp_data is not None:
        if not isinstance(rp_data, dict):
            err("researchPlan 应为对象")
        else:
            check_research_plan(rp_data, err, warn)

    # 通用看板 / 表格 / 环形图
    pre = {}
    root = pathlib.Path(__file__).resolve().parent.parent / "presets"
    for g in ("boards", "tables", "radials"):
        f = root / f"{g}.json"
        pre[g] = json.loads(f.read_text("utf-8")) if f.exists() else {}
    for key, b in (d.get("boards") or {}).items():
        cols = b.get("columns") or (pre["boards"].get(key) or {}).get("columns")
        if not cols:
            err(f"boards.{key} 不是预设，必须自带 columns"); continue
        keys = {c["key"] for c in cols}
        loose = [k for k in b if k in keys | {"hypothesis"} and not isinstance(b[k], dict)]
        if loose:
            warn(f"boards.{key} 把内容写在了 {', '.join(loose)} 字段：渲染时会转成 cards，建议直接写 cards.<列>")
        for ck, arr in (b.get("cards") or {}).items():
            if ck not in keys:
                err(f"boards.{key}.cards 中的列 {ck!r} 不在列定义中（可用：{', '.join(sorted(keys))}）")
            ids(f"boards.{key}.cards.{ck}", arr)
    for key, t in (d.get("tables") or {}).items():
        cols = t.get("columns") or (pre["tables"].get(key) or {}).get("columns")
        if not cols:
            err(f"tables.{key} 不是预设，必须自带 columns"); continue
        keys = {c["key"] for c in cols}
        if not t.get("rows") and (t.get("questions") or t.get("items")):
            warn(f"tables.{key} 用了 {'questions' if t.get('questions') else 'items'} 字段：渲染时会自动转成 rows，建议直接写 rows")
        ids(f"tables.{key}.rows", t.get("rows") or [])
        for i, r in enumerate(t.get("rows") or []):
            extra = [k for k in r if k != "id" and k not in keys]
            if extra:
                warn(f"tables.{key}.rows[{i}] 有不在列定义中的字段（不会显示）：{', '.join(extra)}")
    for key, r in (d.get("radials") or {}).items():
        ids(f"radials.{key}.items", r.get("items") or [])
        if len(r.get("items") or []) > 8:
            warn(f"radials.{key} 超过 8 项，建议保持聚焦")
    return E, W


def check_desk(dr, err, warn, domain_terms=()):
    """deskResearch：研究问题 → 来源 → 综合 → 空白 → 报告。"""
    def ids(path, arr):
        if not isinstance(arr, list):
            err(f"{path} 应为数组"); return []
        seen = set()
        for i, x in enumerate(arr):
            if not isinstance(x, dict):
                err(f"{path}[{i}] 应为对象（含 id 与 text）"); continue
            if not x.get("id"):
                err(f"{path}[{i}] 缺少 id")
            elif x["id"] in seen:
                err(f"{path} 中 id 重复：{x['id']}")
            seen.add(x.get("id"))
        return [x for x in arr if isinstance(x, dict)]
    nonempty = lambda o: isinstance(o, dict) and any(o.get(k) for k in o)

    q = dr.get("query") or {}
    subs = ids("deskResearch.query.subQuestions", q.get("subQuestions") or [])
    sub_ids = {s.get("id") for s in subs}
    for k in ids("deskResearch.query.keywords", q.get("keywords") or []):
        if k.get("subId") and k["subId"] not in sub_ids:
            err(f"deskResearch.query.keywords（{k.get('id')}）的 subId 不存在：{k['subId']}")
    if subs and not q.get("question"):
        warn("deskResearch.query 有子问题但 question 为空")
    if q.get("question") and not 3 <= len(subs) <= 7:
        warn(f"deskResearch.query 有 {len(subs)} 个子问题，建议 4–6 个且互不重叠")
    for s in subs:
        if s.get("angle") != "competitor" and sol_check(s.get("text", ""), domain_terms):
            warn(f"研究子问题含方案词（{sol_check(s['text'], domain_terms)}），可能预设了答案：{s.get('text')}")

    srcs = ids("deskResearch.sources", dr.get("sources") or [])
    src_ids = {s.get("id") for s in srcs}
    for s in srcs:
        nm = s.get("title") or s.get("id")
        for k in ("credibility", "relevance"):
            v = s.get(k, 3)
            if not isinstance(v, (int, float)) or not 1 <= v <= 5:
                err(f"deskResearch.sources（{nm}）的 {k} 应为 1–5 的数字")
        if s.get("status") not in (None, "inbox", "keep", "maybe", "drop"):
            err(f"deskResearch.sources（{nm}）status 只能是 inbox/keep/maybe/drop")
        if s.get("type") not in (None, "report", "gov", "academic", "news", "company", "ugc"):
            err(f"deskResearch.sources（{nm}）type 只能是 report/gov/academic/news/company/ugc")
        if not s.get("title"):
            warn(f"deskResearch.sources（{s.get('id')}）缺少 title")
        if s.get("url") and not re.match(r"^https?://", s["url"]):
            warn(f"deskResearch.sources（{nm}）url 不是 http(s) 链接：{s['url']}")
        if not s.get("url") and s.get("status") == "keep":
            warn(f"deskResearch.sources（{nm}）已采纳但没有 url：无法追溯原始出处")
    if srcs and all((s.get("credibility") or 3) <= 2 for s in srcs):
        warn("deskResearch.sources 全部可信度 ≤ 2：结论缺乏可靠依据，请补充官方统计 / 行业报告 / 论文")

    sy = dr.get("synthesis") or {}
    for k in ("consensus", "divergence", "uncertain"):
        for x in ids(f"deskResearch.synthesis.{k}", sy.get(k) or []):
            bad = [i for i in x.get("sources") or [] if i not in src_ids]
            if bad:
                err(f"deskResearch.synthesis.{k}（{x.get('text', '')[:20]}）引用了不存在的来源：{', '.join(bad)}")
            if k == "consensus" and len(set(x.get("sources") or [])) < 2:
                warn(f"综合矩阵「共识」只有 {len(set(x.get('sources') or []))} 个来源，至少需要 2 个独立来源：{x.get('text', '')[:30]}")
            if x.get("evidence") in ("quote", "observed"):
                warn(f"deskResearch.synthesis.{k} 混入了一手研究证据（{x['evidence']}）：访谈原话 / 观察请放到移情图或洞察聚类")
    if srcs and not nonempty(sy):
        warn("deskResearch.sources 已有来源但 synthesis 为空：请用综合矩阵整理共识 / 分歧 / 不确定")

    gp = dr.get("gaps") or {}
    for k in ("known", "unknown", "toVerify", "actions"):
        arr = ids(f"deskResearch.gaps.{k}", gp.get(k) or [])
        for x in arr:
            bad = [i for i in x.get("sources") or [] if i not in src_ids]
            if bad:
                err(f"deskResearch.gaps.{k}（{x.get('text', '')[:20]}）引用了不存在的来源：{', '.join(bad)}")
            if k == "unknown" and x.get("priority") not in (None, "H", "M", "L"):
                err(f"deskResearch.gaps.unknown（{x.get('text', '')[:20]}）priority 只能是 H/M/L")
            if k == "actions" and x.get("type") not in (None, "desk", "primary"):
                err(f"deskResearch.gaps.actions（{x.get('text', '')[:20]}）type 只能是 desk/primary")

    rp = dr.get("report") or {}
    for k in ("findings", "implications", "actions"):
        for x in ids(f"deskResearch.report.{k}", rp.get(k) or []):
            bad = [i for i in x.get("sources") or [] if i not in src_ids]
            if bad:
                err(f"deskResearch.report.{k}（{x.get('text', '')[:20]}）引用了不存在的来源：{', '.join(bad)}")
            if k == "findings" and not x.get("sources"):
                warn(f"研究报告的发现没有关联来源：{x.get('text', '')[:30]}")
    if nonempty(rp) and not any(gp.get(k) for k in ("known", "unknown", "toVerify")):
        warn("deskResearch.report 已填写但 gaps 为空：报告前请先用「研究空白」说明已知 / 未知 / 需验证")


def check_research_plan(rp, err, warn):
    """researchPlan：假设 → 招募 → 访谈脚本 → 分析 → 追踪。"""
    RISK_SET = {"H", "M", "L"}
    MODE_SET = {"remote", "inperson", "diary", "usability"}
    CRIT_TYPE_SET = {"include", "prefer", "exclude"}
    QTYPE_SET = {"open", "probe", "scenario", "close"}

    def items(path, arr):
        """提取数组中的 dict 元素，同时检查 id 存在性。"""
        if not isinstance(arr, list):
            err(f"{path} 应为数组"); return []
        seen = set()
        result = []
        for i, x in enumerate(arr):
            if not isinstance(x, dict):
                continue
            if not x.get("id"):
                err(f"{path}[{i}] 缺少 id")
            elif x["id"] in seen:
                err(f"{path} 中 id 重复：{x['id']}")
            seen.add(x.get("id"))
            result.append(x)
        return result

    # ① 假设清单
    hyps = items("researchPlan.hypotheses", rp.get("hypotheses") or [])
    if not hyps:
        warn("researchPlan.hypotheses 为空：至少需要 1 条研究假设")
    for h in hyps:
        if h.get("risk") and h.get("risk") not in RISK_SET:
            err(f"researchPlan.hypotheses（{h.get('id')}）risk 只能是 H/M/L")
        if not h.get("text"):
            warn(f"researchPlan.hypotheses（{h.get('id')}）text 为空")
    if hyps and not any(h.get("selected") for h in hyps):
        warn("researchPlan.hypotheses 没有任何假设被 selected：研究计划应标记本轮验证的假设")

    # ② 招募方案
    rec = rp.get("recruit") or {}
    n = rec.get("n")
    if n is not None and not (isinstance(n, int) and n > 0):
        err(f"researchPlan.recruit.n 应为正整数，当前为 {n!r}")
    mode = rec.get("mode")
    if mode is not None and mode not in MODE_SET:
        err(f"researchPlan.recruit.mode 只能是 remote/inperson/diary/usability，当前为 {mode!r}")
    for c in items("researchPlan.recruit.criteria", rec.get("criteria") or []):
        if c.get("type") and c.get("type") not in CRIT_TYPE_SET:
            err(f"researchPlan.recruit.criteria（{c.get('id')}）type 只能是 include/prefer/exclude")

    # ③ 访谈脚本
    script = rp.get("script") or {}
    for sec in ("warmup", "main", "wrap"):
        for q in items(f"researchPlan.script.{sec}", script.get(sec) or []):
            if q.get("type") and q.get("type") not in QTYPE_SET:
                err(f"researchPlan.script.{sec}（{q.get('id')}）type 只能是 open/probe/scenario/close")
            if q.get("type") == "close":
                warn(f"researchPlan.script.{sec}（{q.get('id')}）是封闭式提问（close），定性访谈应优先用开放式问题")
    if not (script.get("main") or []):
        warn("researchPlan.script.main 为空：核心问题尚未填写")


def main(a):
    if len(a) != 1:
        sys.exit(__doc__)
    try:
        d = json.loads(pathlib.Path(a[0]).read_text("utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误：第 {e.lineno} 行第 {e.colno} 列：{e.msg}"); sys.exit(1)
    E, W = check(d)
    for x in E: print("❌", x)
    for x in W: print("⚠️ ", x)
    print(f"检查完成：{len(E)} 个错误，{len(W)} 个提醒" if E or W else "✓ 检查通过")
    sys.exit(1 if E else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
