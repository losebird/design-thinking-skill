# Changelog

## 1.2.0 — 2025-07
### 功能增强
- **#7 复制给 AI 精简**：「复制给 AI」只发本页路径数据 + meta，减少发给 AI 的 token；dashboard/overview 仍含完整数据。
- **#8 validate 增强**：新增 `researchPlan` 结构校验（假设 risk/selected、招募 n/mode/criteria.type、脚本 type/close 告警、main 为空提醒）；`SOL` 方案词检查支持 `meta.domainTerms` 白名单。
- **#9 out() 精简**：导出时裁剪空结构（null/""/[]/{}，保留 0/false）；`meta._vchecked` 改存 localStorage，不再污染 JSON 导出。
- **#10 无障碍**：`ed()` 新增 `role="textbox"`、`aria-multiline`、`aria-label`；dashboard/research-plan 的裸 `navigator.clipboard` 调用统一改用 `DT.copy()`。
- **#11 CI**：新增 `.github/workflows/check.yml`（build 自检、validate、render、XSS 注入、页面结构检查）；`render.py --all` 自动清理过期 HTML；新增 `dev/xss.py`；check.mjs 支持多目录参数。

## 1.1.0 — 2025-07
### 架构重构
- 新建根目录 `tools.json` 作为 41 个工具的唯一注册表（phases + tools）。
- `_base.js` 中 PATHS/TOPS 由注册表派生；`build.py` 注入注册表、自检、同步工具数。
- dashboard/overview 工具卡片从注册表驱动；render.py/validate.py 的 PAGES/KNOWN_TOP 也从注册表读取。
- 文档：empathize/define/prompts/README 更新，刷新截图。

## 1.0.0 — 2025-07
### 初始版本
- 5 个桌面研究页面（research-query / source-board / synthesis / gap-analysis / research-report）。
- `deskResearch` schema、validate 检查、dashboard/overview 接入。
- `_base.js` 新增 `aiPanel/ctx/srcPick`；`importData` 深度合并。
