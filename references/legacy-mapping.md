# 旧编号与旧清单映射

> 版本: v1.0.0
> 更新日期: 2026-11-17

| 版本 | 日期 | 修改说明 | 作者 |
|---|---|---|---|
| v1.0.0 | 2026-11-17 | 建立 v1.3/v1.4 条款、附录一与 18/22 条自查到当前章节的映射 | Doubao |

本表用于解析外部文档、历史审计和旧偏好中的旧引用，不恢复旧编号作为稳定入口。当前稳定锚点为 `SKILL.md` 的 `PS-B1`–`PS-B6`；引用具体操作时优先使用“文件 + 章节标题”，而不是旧条款号。

## 1. 旧条款映射（v1.3/v1.4 → v1.5/v1.6）

| 旧编号 | 旧主题 | 当前位置 |
|---|---|---|
| 第一条 | 目录结构保护 | `SKILL.md` PS-B1；`references/authoring.md` 文件职责与命名 |
| 第二条 | 文件归类存放规范 | `SKILL.md` PS-B1；`references/authoring.md` 文件职责与命名 |
| 第三条 | 脚本头部注释与参数管理 | `references/authoring.md` 脚本头部与集中参数 |
| 第四条 | 版本号与更新日期管理 | `references/authoring.md` 版本、日期与编码 |
| 第五条 | 主线逻辑维护原则 | `SKILL.md` PS-B1；`references/authoring.md` 文件职责与命名 |
| 第六条 | 阶段工作回头自检（阶段门） | `references/workflows.md` 阶段交付与依赖验收；阶段门文件命名与看板 |
| 第七条 | 路径可移植性 | `references/authoring.md` 路径与输入保护 |
| 第八条 | 跨位置工作与主目录归属 | `SKILL.md` PS-B4；`references/authoring.md` 归档与证据 |
| 第九条 | 编码统一规范 | `references/authoring.md` 版本、日期与编码 |
| 第十条 | 命名规范 | `references/authoring.md` 文件职责与命名 |
| 第十一条 | Git 版本控制 | `references/git-decisions.md` |
| 第十二条 | 大文件与 `.gitignore` 管理 | `references/git-decisions.md` |
| 第十三条 | 临时文件管理 | `references/authoring.md` 文件职责与命名；`references/git-decisions.md` |
| 第十四条 | 原始数据只读保护 | `SKILL.md` PS-B2；`references/authoring.md` 路径与输入保护 |
| 第十五条 | 审查/审计文档归档约定 | `references/authoring.md` 归档与证据 |
| 附录一 | 项目启动流程清单（Bootstrap Checklist） | `references/workflows.md` 新项目启动 |
| 18 条自查清单（v1.3） | 提交前逐项自查 | `references/workflows.md` 按任务和风险选择自查；本文件第 2 节 |
| 22 条自查清单（v1.4） | 提交前逐项自查 | 同上 |

## 2. 18/22 条自查的分类映射

v1.3 的 18 条与 v1.4 的 22 条不是逐条对应到当前某一节；v1.5/v1.6 改为“按任务和风险选择适用项”。按主题归类如下：

| 旧清单主题 | 当前检查位置 |
|---|---|
| 根目录与文件归类 | `SKILL.md` PS-B1；`references/authoring.md` 文件职责与命名 |
| 脚本头注释与参数集中 | `references/authoring.md` 脚本头部与集中参数 |
| 版本、日期、修改记录 | `references/authoring.md` 版本、日期与编码 |
| 主线逻辑与补丁目录 | `SKILL.md` PS-B1；`references/authoring.md` 文件职责与命名 |
| 阶段门四维与记录 | `references/workflows.md` 阶段交付与依赖验收、阶段自检记录模板 |
| 路径可移植与根锚点 | `references/authoring.md` 路径与输入保护 |
| 跨位置归属与同步 | `SKILL.md` PS-B4；`references/authoring.md` 归档与证据 |
| 编码、BOM、CRLF、乱码 | `references/authoring.md` 版本、日期与编码；`scripts/check_text_health.py` |
| 命名规范 | `references/authoring.md` 文件职责与命名 |
| Git 状态、暂存保护、提交建议 | `references/git-decisions.md` 只读状态快照、建议与执行分开 |
| 大文件与 `.gitignore` | `references/git-decisions.md` |
| 临时文件与清理授权 | `references/authoring.md` 文件职责与命名；`references/git-decisions.md` |
| 原始数据只读 | `SKILL.md` PS-B2；`references/authoring.md` 路径与输入保护 |
| 审计/审查归档 | `references/authoring.md` 归档与证据 |
| 新项目启动（骨架、README、Git、忽略） | `references/workflows.md` 新项目启动 |
| 证据与结论对应、未执行标注 | `SKILL.md` PS-B6；`references/workflows.md` 按任务和风险选择自查 |

## 3. 引用写法

- 当前规则：`project-spec PS-B2`，或 `references/git-decisions.md 的“嵌套独立仓库与文章级冻结”`。
- 旧文档：保留原引用，并在旁边加“对应当前位置：……”，不静默改写历史结论。
- 不确定映射时，先按主题在 `SKILL.md` 与 `references/` 中检索；仍找不到就写“未映射”，不要编造条款号。
