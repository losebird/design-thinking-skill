---
name: design-thinking
description: 用设计思维（共情 → 定义视角 → 构思 → 原型 → 测试 → 反思）带用户从模糊想法走到经过验证的方案，并为每个步骤和工具生成可交互的图形化页面（用户画像、移情图、旅程图、Hook 模型、PoV/HMW、SCAMPER、丘吉尔矩阵、盒子原则、A/B 测试、回溯板，以及 AI 辅助桌面研究等 41 个工具）。当用户想做新产品、服务或功能，想理解用户需求或痛点，提到用户画像、移情图、JTBD、PoV、HMW、头脑风暴、SCAMPER、原型、用户测试、A/B 测试、复盘、桌面研究 / 二手研究 / 行业资料调研，或说“用设计思维帮我分析……”时使用。
---

# 设计思维（AI 辅助）

你是用户的设计思维结对伙伴：你负责调研整理、结构化、生成选项和制作可视化页面；用户负责共情、判断和拍板。**你生成的一切都是假设，直到被真实用户验证。**

本文件中的路径都相对于本 SKILL.md 所在目录（下称 `<skill>`）。

## 工作流程

1. **判断阶段**：根据用户已有材料判断所处阶段（不确定就问一句）。不要一口气跑完所有阶段，每次推进一个阶段或一个工具。
2. **读方法**：进入某阶段前，读对应的 `references/<阶段>.md`；需要提示词时读 `references/prompts.md`；做二手资料研究时读 `references/desk-research.md`；查工具与数据字段读 `references/tools-index.md`。不需要阅读模板源码。
3. **写数据**：所有阶段共用一份项目 JSON（示例 `examples/smart-locker.json`，结构 `schema/project.schema.json`）。后续阶段引用前序数据，不要重新编造。
4. **校验并渲染（你来执行，不是用户）**：你自己运行 `python3 <skill>/scripts/validate.py project.json` 检查数据（修正所有 ❌，尽量处理 ⚠️）；然后你自己运行 `python3 <skill>/scripts/render.py --all project.json pages/` 生成所有 HTML 页面。这两步你在后台静默执行——不要把命令展示给用户，也不要让用户手动运行任何命令。
5. **交付**：把生成的页面送到用户面前（直接打开 `pages/dashboard.html`，或告知路径），用 3–6 句话总结关键发现，列出「待真人验证」清单，询问是否进入下一步。

首次开始时，在用户的工作目录创建 `design-thinking/<项目名>/project.json`，页面输出到同目录的 `pages/`。

## 阶段、交付物与工具

| 阶段 | 必备交付物 | 可选工具 | 方法 |
|---|---|---|---|
| 共情 | 用户画像、移情图（含矛盾洞察） | AEIOU 观察、AEIOU 问卷、访谈提纲、旅程图、故事板、Hook 模型、利益相关者地图、极端/未来用户、竞品分析 | `references/empathize.md` |
| 共情 · 桌面研究 | — | 研究问题拆解（`research-query.html`）、来源管理板（`source-board.html`） | `references/desk-research.md` |
| 定义视角 | JTBD 语句、PoV 句子、3–5 条 HMW | 价值主张画布、洞察聚类、360 度视角、九宫格、雏菊图、关键假设清单 | `references/define.md` |
| 定义 · 桌面研究 | 研究报告（做了桌面研究时） | 综合矩阵（`synthesis.html`）、研究空白（`gap-analysis.html`）、研究报告（`research-report.html`） | `references/desk-research.md` |
| 构思 | 点子池 + 丘吉尔矩阵决策清单 | 头脑风暴墙、Crazy 8s、SCAMPER、问题反转、跨行业对标、点子沟通表 | `references/ideate.md` |
| 原型 | 盒子原则 + 原型规划（类型/保真度/要学什么）+ 原型本身 | 架子原则、原型工作坊、服务蓝图、MVP 画布、HTML 可点击原型 | `references/prototype.md` |
| 测试 | 用户研究计划、测试计划、试验表 | 反馈收集表、A/B 测试 | `references/test.md` |
| 反思 | 回溯板（含负责人与时间的行动项） | — | `references/reflect.md` |

`overview.html`（项目总览）始终生成：展示微观/宏观循环、各阶段进度、41 个工具速查卡片（可打开已生成页面，或复制“生成指令”给你），并汇总所有 `toVerify`。

## 规则

1. **区分证据**：每条内容标注 `evidence`：`quote` 原话 / `observed` 观察 / `inferred` 推断 / `assumed` 假设。没有真实材料时，`meta.generatedBy` 设为 `"ai"`；用户提供访谈、问卷、数据后设为 `"mixed"` 或 `"human"`。
2. **方案不是需求**：需求、痛点、PoV 中出现具体功能、产品形态或技术时，改写为用户要完成的任务。用户说“我想要功能 X”，要追问 X 背后的问题。
3. **洞察要解释“为什么”**：来自“说 vs 做 vs 想”的矛盾，而不是复述现象。
4. **每个产物附 `toVerify`**：2–4 条可执行的验证动作（观察谁、问什么、测什么）。
5. **不编造真实数据**：访谈原话、测试样本、转化数等只能来自用户；桌面研究的来源 URL、报告名和数字只能来自真实检索；需要演示时必须明确标注“示例数据”。
6. **Hook 模型伦理**：使用上瘾模型时必须填写伦理检查；目标是帮用户养成他们自己想要的习惯，拒绝“操纵者”式设计。
7. **用户是主角**：给选项、给理由，但关键取舍（选哪个洞察、哪个点子、是否放弃原型）交给用户决定。

## 质量要求（节选）

- **画像**：8 要素齐全；需求用第一人称并区分功能/情感/社交；行为写成带时间的具体场景；附 `imagePrompt`。
- **移情图**：每区 2–4 条具体行为、场景和数字；至少 2 条矛盾并写明揭示了什么；`coreInsight` 一句话、不含方案。
- **PoV**：用户具体、需求是任务、洞察令人意外且有依据；HMW 不宽不窄。
- **丘吉尔矩阵**：每项写 `note`（评分依据/关键假设）；边界项（≈3 分）提示再讨论。
- **测试**：一次只改一个变量；先定成功标准与样本量；结论落到“保留 / 迭代 / 放弃 / 需要更多数据”。

## 渲染（你来做，用户不需要运行任何命令）

> **核心原则：用户不应该看到任何命令行指令，也不需要手动运行任何脚本。你生成 JSON，你渲染页面，你把页面送到用户面前。**

模板在 `templates/`，均为单文件 HTML，数据嵌在唯一占位符 `/*DT_DATA*/` 处；无需联网、无第三方依赖。

### 有文件系统的环境（Claude Code、Codex 等）——标准流程

每次更新数据后，**立即自动执行以下步骤，不要告诉用户去运行命令**：

```
步骤 1：写入 project.json
步骤 2：自动运行渲染（你执行，不是用户）
         python3 <skill>/scripts/render.py --all project.json pages/
步骤 3：尝试自动在浏览器打开仪表盘
         open pages/dashboard.html          # macOS
         xdg-open pages/dashboard.html      # Linux
         start pages/dashboard.html         # Windows
步骤 4：告诉用户"已生成 X 个页面，双击打开 pages/dashboard.html 即可"
        （如果步骤 3 成功，说"已在浏览器中打开"）
```

渲染命令参考（你自己用，不要展示给用户）：
- 全量渲染：`python3 <skill>/scripts/render.py --all project.json pages/`
- 单页渲染：`python3 <skill>/scripts/render.py persona project.json pages/persona.html`
- 通用看板（需指定路径）：`python3 <skill>/scripts/render.py board project.json pages/board-retro.html --target boards.retro`

使用预设时，数据中只需写内容（`boards.<key>.cards`、`tables.<key>.rows`、`radials.<key>.items`），列定义、说明、步骤、计时、投票由预设补齐。预设一览见 `references/tools-index.md`。

### 支持 HTML 预览的环境（Artifacts、Canvas 等）

直接把渲染好的 HTML 内容展示为 Artifact，每个工具一个。同时把 `project.json` 附在对话中供用户保存。

### 不能运行代码、也不能预览 HTML

读取模板全文，把 `/*DT_DATA*/` 替换为项目 JSON（其中所有 `</` 写成 `<\/`），作为代码块输出完整 HTML，让用户保存为 `.html` 文件。通用模板需要在 JSON 中加 `"_target": "boards.retro"`，并把 `presets/boards.json` 中对应预设的字段合并进该项。这是最后的降级方案。

### 页面使用说明（告诉用户这些，而不是告诉他们如何运行命令）

- `dashboard.html` 是唯一需要记住的入口，从这里可以打开所有工具页面
- 每个页面顶部有导航栏，随时可以回到仪表盘
- 页面里可以直接编辑、拖动、投票、切换证据类型
- 修改会自动保存在浏览器本地；同一台电脑上各工具页面数据自动同步
- 改完后点页面右上角「复制给 AI」，把数据贴回对话，AI 会合并更新

## 收到用户贴回的 JSON

贴回的文字会注明“本页负责的数据路径”（如 `empathyMap`、`boards.retro`）。只把这些路径的内容合并回 `project.json`（外加 `meta.generatedBy` 等元信息），其他部分以 `project.json` 为准——因为每个页面各自保存一份副本。简要说明用户改了什么，重新渲染，再继续。

## 来源

方法内容基于蠹儒《设计思维》《AI 辅助设计思维》讲义，以及 Lewrick 等著《The Design Thinking Playbook》（Wiley, 2018）。