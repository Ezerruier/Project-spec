# project-spec v1.6.0 升级验收记录

> 版本: v1.0.0
> 更新日期: 2026-11-17

| 版本 | 日期 | 修改说明 | 作者 |
|---|---|---|---|
| v1.0.0 | 2026-11-17 | 记录 v1.6.0 的变更范围、验证证据、边界与未验证项 | Doubao |

## 1. 基线与范围

- 基线：v1.5.0，提交 `6215d33`，`SKILL.md` 10,109 bytes。
- 本次目标：按复盘报告推荐的 P0/P1 项落地，保持技能定位、默认不初始化 Git、不默认改 `.gitignore`、不默认提交的边界。
- 变更范围：`SKILL.md`、`README.md`、`references/authoring.md`、`collaboration.md`、`git-decisions.md`、`workflows.md`、新增 `references/legacy-mapping.md`、新增 `scripts/check_text_health.py`、更新 `scripts/verify_upgrade.py`、本记录。
- 未改动：`references/workspace-organization.md`（本轮无新增内容需要写入）、历史版本记录原文、任何真实项目文件。

## 2. 变更清单

| 编号 | 变更 | 文件 |
|---|---|---|
| PS-01 | 宿主平台委派限制优先于“主动协作” | `SKILL.md` 适用范围与优先级；`references/collaboration.md` |
| PS-02 | 稳定边界锚点 PS-B1–PS-B6；旧条款、附录一、18/22 条自查映射 | `SKILL.md`；`references/legacy-mapping.md`；`README.md` |
| PS-03 | 只读文本健康检查脚本与流程步骤 | `scripts/check_text_health.py`；`references/authoring.md`；`references/git-decisions.md`；`references/workflows.md`；`SKILL.md` |
| PS-04 | 常驻偏好改为场景化表述 | 偏好 `p1_AQDGW4AOalA`（技能外） |
| PS-05 | 嵌套独立仓库与文章级冻结清单 | `references/git-decisions.md`；`SKILL.md` |
| PS-06 | 阶段门命名与 gate dashboard | `references/workflows.md`；`SKILL.md` |
| PS-07 | 状态陈述 as-of 与只读仓库健康快照 | `references/authoring.md`；`references/git-decisions.md` |
| X-01 | `docs/prompts/` 提示词归档目录 | `references/authoring.md`；`references/workflows.md` |

## 3. 实际验证

| 检查 | 结果 | 证据 |
|---|---|---|
| 静态 Markdown、版本/日期/修改记录、本地链接、代码围栏、行尾空白 | PASS：10 个 Markdown、52 个本地链接、0 暂存改动；Git fixture PASS | `scripts/verify_upgrade.py` |
| 文本健康检查（UTF-8、BOM、CRLF、NUL、乱码、`.gitignore` 红线） | 14 个文件，0 error，0 warning（`--strict`） | `scripts/check_text_health.py . --gitignore --strict` |
| Python 语法 | `py_compile=PASS` | `python -m py_compile scripts/*.py` |
| 真实 `.gitignore` 只读副本 | 1 error（第 35 行非法 UTF-8）、4 warning（CRLF、`logs/`、`*.log`、`archive/`） | `MRI-Analysis/.gitignore` 只读副本 |
| 链接可达性 | PASS：52 条本地链接均存在 | `scripts/verify_upgrade.py` |
| 核心入口大小 | 22,841 → 11,415 bytes（相对 v1.4 基线减少 50.0%） | `scripts/verify_upgrade.py` |

## 4. 边界与未验证项

- 未修改 `MRI-Analysis`、`gut-suicide-meta-mr` 的任何文件；`.gitignore` 检查只使用只读副本或临时目录。
- 未验证跨平台（Linux/macOS）运行；`check_text_health.py` 只用 Python 标准库，但 Windows 路径与 Git 可执行文件差异未逐一测试。
- 未验证 GitHub 远端最新提交；推送前以 `git status`、`git log` 和远端 `origin/main` 为准。
- 未对历史项目批量重命名阶段门文件；只提供新命名与 dashboard 规则。
- 未恢复旧编号作为稳定入口；只提供映射表。

## 5. 提交建议

- 建议将本记录与代码、文档变更作为一组提交；提交说明写清“改了什么、为什么、验证了什么、未验证什么”。
- 提交、推送、发布分别判断授权；本次用户已要求上传 GitHub，推送前仍需核对认证与远端状态。
