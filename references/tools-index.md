# 工具索引：工具 → 页面 → 数据

渲染：`python3 scripts/render.py <模板> <数据.json> <输出.html> [--target 路径]`，或 `--all <数据.json> <目录>` 一次生成全部。通用模板（board/table/radial）的预设见 `presets/`，用 `--list` 查看、`--preset boards.retro` 打印。数据只需写 `cards` / `rows` / `items`，预设会自动补齐列定义与说明。

<!-- tools:start（由 dev/build.py 根据 tools.json 生成，请勿手改） -->
| 阶段 | 工具 | 模板 / 输出文件 | 数据路径 | 方法 |
|---|---|---|---|---|
| 全程 | 项目仪表盘（入口） | dashboard / dashboard.html | 整个项目 | SKILL.md |
| 全程 | 项目总览 + 工具速查 | overview / overview.html | 整个项目 | 本文件 |
| 共情 | 用户画像 Persona | persona / persona.html | `personas`、`personaSteps` | empathize.md §4 |
| 共情 | 移情图 Empathy Map | empathy-map / empathy-map.html | `empathyMap` | empathize.md §5 |
| 共情 | 顾客旅程图 | journey / journey.html | `journey` | empathize.md §6 |
| 共情 | Hook 上瘾模型 | hook / hook.html | `hook` | empathize.md §7 |
| 共情 | AEIOU 观察 | board / board-aeiou.html | `boards.aeiou` | empathize.md §3 |
| 共情 | 访谈提纲 | table / table-interview.html | `tables.interview` | empathize.md §2 |
| 共情 | AEIOU 问卷 | table / table-survey.html | `tables.survey` | empathize.md §3 |
| 共情 | 利益相关者地图 | radial / radial-stakeholders.html | `radials.stakeholders` | empathize.md §1 |
| 共情 | 极端 / 未来用户 | table / table-extremes.html | `tables.extremes` | empathize.md §8 |
| 共情 | 故事板 Storyboard | storyboard / storyboard.html | `storyboard` | empathize.md §6 |
| 共情 | 竞品分析 | table / table-competitors.html | `tables.competitors` | empathize.md §9 |
| 共情 | 研究问题拆解 | research-query / research-query.html | `deskResearch.query` | desk-research.md §2.1 |
| 共情 | 来源管理板 | source-board / source-board.html | `deskResearch.sources` | desk-research.md §2.2 |
| 定义 | JTBD → PoV → HMW | pov / pov.html | `define` | define.md §3–6 |
| 定义 | 价值主张画布 | value-canvas / value-canvas.html | `valueCanvas` | define.md §2 |
| 定义 | 洞察聚类 | board / board-insights.html | `boards.insights` | define.md §1 |
| 定义 | 360 度视角 | radial / radial-view360.html | `radials.view360` | define.md §2 |
| 定义 | 九宫格 | board / board-ninegrid.html | `boards.ninegrid` | define.md §2 |
| 定义 | 雏菊图 | radial / radial-daisy.html | `radials.daisy` | define.md §2 |
| 定义 | 关键假设清单 | table / table-assumptions.html | `tables.assumptions` | define.md §2 |
| 定义 | 综合矩阵 | synthesis / synthesis.html | `deskResearch.synthesis` | desk-research.md §2.3 |
| 定义 | 研究空白 | gap-analysis / gap-analysis.html | `deskResearch.gaps` | desk-research.md §2.4 |
| 定义 | 研究报告 | research-report / research-report.html | `deskResearch.report` | desk-research.md §2.5 |
| 构思 | 丘吉尔矩阵 | matrix / matrix.html | `ideate.matrix` | ideate.md §9 |
| 构思 | SCAMPER 奔驰法 | scamper / scamper.html | `ideate.scamper`、`ideate.matrix` | ideate.md §4 |
| 构思 | Crazy 8s | board / board-crazy8.html | `boards.crazy8` | ideate.md §3 |
| 构思 | 头脑风暴墙 | board / board-brainstorm.html | `boards.brainstorm` | ideate.md §3 |
| 构思 | 问题反转 | table / table-reversal.html | `tables.reversal` | ideate.md §5 |
| 构思 | 跨行业对标 | table / table-analogy.html | `tables.analogy` | ideate.md §6 |
| 构思 | 点子沟通表 | table / table-ideas.html | `tables.ideas` | ideate.md §8 |
| 原型 | 盒子原则 + 保真度 | box / box.html | `prototype` | prototype.md §2–4 |
| 原型 | 架子原则 | board / board-shelf.html | `boards.shelf` | prototype.md §5 |
| 原型 | 原型工作坊 | board / board-workshop.html | `boards.workshop` | prototype.md §6 |
| 原型 | MVP 画布 | board / board-mvp.html | `boards.mvp` | prototype.md §4 |
| 原型 | 服务蓝图 | table / table-blueprint.html | `tables.blueprint` | prototype.md §2 |
| 测试 | 用户研究计划 | research-plan / research-plan.html | `researchPlan` | test.md §1 |
| 测试 | A/B 测试 | ab-test / ab-test.html | `test.ab` | test.md §4 |
| 测试 | 测试计划 | table / table-testplan.html | `tables.testplan` | test.md §2 |
| 测试 | 反馈收集表 | board / board-feedback.html | `boards.feedback` | test.md §3 |
| 测试 | 试验表 | table / table-experiments.html | `tables.experiments` | test.md §5 |
| 反思 | 回溯板 | board / board-retro.html | `boards.retro` | reflect.md |
<!-- tools:end -->

只有方法、没有专门页面的：发言棒、正念、WH 问题（并入访谈提纲）、草图、理想原型、MVP。需要时可自建 `boards.<新key>` / `tables.<新key>`（自带 `title`、`columns`），通用模板同样能渲染。

## 数据格式速查
完整示例：`examples/smart-locker.json`；结构定义：`schema/project.schema.json`。所有列表项都带唯一 `id`（如 `"s1"`）。

```jsonc
{
  "meta": {"project": "项目名", "challenge": "设计挑战", "phase": "empathize|define|ideate|prototype|test|reflect",
           "macro": "diverge|pivot|converge", "generatedBy": "ai|mixed|human"},
  "personas": [{"id":"p1","name":"","avatar":"emoji","image":"图片URL","snapshot":"年龄 · 城市 · 职业 · 收入 · 家庭",
     "tags":[""],"jobs":{"functional":"","emotional":"","social":""},"pains":[{"id":"","text":""}],
     "behaviors":[{"time":"08:20","action":""}],"motivation":"","quote":"","imagePrompt":""}],
  "personaSteps": [{"done": true}],                       // 10 项，对应 10 步
  "empathyMap": {"personaId":"p1","view":"simple|full",
     "sees|hears|says|does|thinks|feels|pains|gains":[{"id":"s1","text":"","evidence":"quote|observed|inferred|assumed"}],
     "contradictions":[{"a":"s1","b":"d1","insight":""}],"coreInsight":"","toVerify":[""]},
  "journey": {"personaId":"p1","scenario":"","stages":[{"id":"","name":"","actions":"","touchpoints":"","thoughts":"",
     "emotion":-2,"pains":"","opportunities":""}]},       // emotion: -2..2
  "hook": {"product":"","trigger":{"external":"","internal":""},"action":{"behavior":"","ability":""},
     "reward":{"tribe":"","hunt":"","self":""},"investment":{"what":"","next":""},"bmat":{"m":3,"a":3,"t":3},
     "ethics":{"improves":"yes|no","selfUse":"yes|no"}},
  "define": {"insights":[{"id":"","text":"","votes":0,"selected":false}],
     "jtbd":{"situation":"","motivation":"","outcome":"","functional":"","emotional":"","social":""},
     "pov":{"format":"standard|story|storyPain|hmw","user":"","need":"","insight":"","benefit":"","pain":""},
     "hmw":[{"id":"","text":"","star":false}]},
  "ideate": {"scamper":{"subject":"","S":[{"id":"","text":"","star":false}],"C":[],"A":[],"M":[],"P":[],"E":[],"R":[]},
     "matrix":{"mode":"value|urgency","items":[{"id":"","from":"来源点子id","text":"","x":1,"y":1,"note":"依据/假设"}]}},
                                                          // x=可行性或紧迫 1-5, y=价值或影响 1-5
  "prototype": {"box":{"type":"问题盒子|解决方案盒子|项目盒子|流程盒子","logo":"emoji","name":"","slogan":"",
     "color":"blue|green|orange|red|purple|teal|pink|gray","benefits":[{"id":"","text":""}],"features":[{"id":"","text":""}],
     "who":"","which":"","when":"","where":"","why":"","price":"","company":""},
     "plan":{"kind":"physical|service|digital","fidelity":0,"learn":"","core":"","rules":[true,false,false]}},
  "test": {"ab":{"name":"","hypothesis":"","variable":"","metric":"","a":{"label":"","desc":"","n":0,"conv":0},
     "b":{"label":"","desc":"","n":0,"conv":0},"alpha":0.05,"power":0.8,"baseline":10,"mde":20}},
  "boards": {"<key>": {"cards": {"<列key>": [{"id":"","text":"","votes":0}]}, "actions":[{"id":"","text":"","owner":"","due":"YYYY-MM-DD","done":false}], "step":0}},
  "tables": {"<key>": {"rows": [{"id":"", "<列key>": "值"}]}},   // rows 也可写成 questions（如 survey）
  "radials": {"<key>": {"center":"", "items": [{"id":"","label":"","text":""}]}}   // items 也可写成 petals，格式相同
}
```
自定义看板/表格时补充：board `{title,en,intro,cols,columns:[{key,title,hint,color}],voting:{enabled,perPerson},timer:{minutes},steps:[],actionsEnabled}`；table `{title,en,intro,rowLabel,columns:[{key,label,type:"text|long|select|number|check|date",options,colors,width,placeholder}]}`。
