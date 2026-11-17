# 脚本与文档编写参考

> 版本: v1.0.1
> 更新日期: 2026-11-17

| 版本 | 日期 | 修改说明 | 作者 |
|---|---|---|---|
| v1.0.0 | 2026-11-08 | 收敛语言模板、参数、路径、元信息与归档要求 | Codex |
| v1.0.1 | 2026-11-17 | 增加 docs/prompts/、状态陈述 as-of 与编码检查说明 | Doubao |

新增或实际修改脚本、分析说明、阶段记录及审计文档时读取；只选与本次文件有关的部分。遵守 [核心规则](../SKILL.md)，不为套模板批量改造历史文件或工具生成文件。普通小修改直接完成相关检查，不触发整套启动、整理或阶段流程。

## 文件职责与命名

沿用项目已明确的职责和软件原生布局。新项目按需使用 `scripts/`（入口脚本）、`src/`（模块）、`docs/`（说明；可细分 `docs/prompts/` 存放可复用提示词与执行指令）、`data/`（数据）、`figures/`（成品图）、`tests/`（测试）、`scratch/` 或 `tmp/`（临时产物）；不要为凑齐骨架创建空目录。根目录保留核心入口、总览和工具必需配置，临时检查结果不散落其中。

新增目录和代码文件优先英文命名：目录及 Bash 用 kebab-case，Python 用 snake_case，R 用项目已有风格，PowerShell 用 `Verb-Noun.ps1`。排序前缀及分隔符保持项目内一致；文档正文和成品文档可用中文。不用 `_v2`、`_final` 等目录复制替代版本管理；确有不同职责的产物应以用途命名。重名不构成合并、删除或迁移历史文件的授权。

临时产物使用明确目录或用途名，收尾按已有生命周期和删除授权处理；不得仅凭 `_` 前缀认定无用。临时目录是否加入忽略规则按 [Git 决策](git-decisions.md)评估，不能因本参考自动创建或修改 `.gitignore`。

## 脚本头部与集中参数

本次新增或实际修改的独立分析脚本在头部维护 `Name / Description / Author / Version / Update / Usage`，按需增加 `Dependencies / Changelog`。已有包、模块或工具约定可使用其等效元信息，避免重复维护两套版本。作者按实际贡献填写，不猜测身份。`Description` 交代读写边界；模板只展示头部，不代表分析已实现或验证。

**Bash**：

```bash
#!/usr/bin/env bash
# Name        : analyze.sh
# Description : 只读输入数据；仅向指定输出目录写分析结果
# Author      : NAME
# Version     : 1.0.0
# Update      : YYYY-MM-DD
# Usage       : bash scripts/analyze.sh INPUT_PATH OUTPUT_DIR
```

**Python**：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Name        : analyze.py
# Description : 只读输入数据；仅向指定输出目录写分析结果
# Author      : NAME
# Version     : 1.0.0
# Update      : YYYY-MM-DD
# Usage       : python scripts/analyze.py --input INPUT_PATH --output OUTPUT_DIR
# Dependencies: 按实际依赖填写
```

**R**：

```r
#!/usr/bin/env Rscript
# Name        : analyze.R
# Description : 只读输入数据；仅向指定输出目录写分析结果
# Author      : NAME
# Version     : 1.0.0
# Update      : YYYY-MM-DD
# Usage       : Rscript scripts/analyze.R INPUT_PATH OUTPUT_DIR
```

**PowerShell**：

```powershell
# Name        : Export-Report.ps1
# Description : 只读输入数据；仅向指定输出目录写报告
# Author      : NAME
# Version     : 1.0.0
# Update      : YYYY-MM-DD
# Usage       : ./scripts/Export-Report.ps1 -InputPath INPUT_PATH -OutputDir OUTPUT_DIR
```

关键路径、阈值、随机种子和分析选项在脚本开头的配置或参数解析区集中定义，说明单位、默认值、允许范围和选择理由；避免散落的魔法常量。允许使用已有共享配置或命令行解析器，不另造平行配置。检查参数合法性及输入、输出位置后再写入；对可能覆盖的既有结果遵守当前授权。仅做路径或目录适配时，不顺带改变科学参数、队列或处理顺序。

## 路径与输入保护

项目内默认输入输出基于已核实的项目根目录拼接，外部数据、工具和输出位置由参数、配置或环境变量传入，不能写死个人盘符或机器路径。脚本目录不一定是项目根目录；需明确相对层级或根标识，并支持显式覆盖。

| 语言 | 获取锚点的可选方式与适用条件 |
|---|---|
| Python | 普通脚本可用 `Path(__file__).resolve().parent`；交互环境没有 `__file__` 时显式传入根目录 |
| Bash | 普通脚本可用 `SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"`；软链接入口需按项目约定处理真实位置 |
| PowerShell | 脚本使用 `$PSScriptRoot`；交互运行应显式传入根目录 |
| R | `Rscript` 入口可从 `commandArgs(trailingOnly = FALSE)` 的 `--file=` 参数定位脚本；`source()` 或交互模式优先显式传根目录。已使用 `here` 的项目可维护已确认的根锚点，不假定工作目录就是项目根 |

迁移或改动根锚点后，核对不同工作目录启动、命令行覆盖、清单的生产与消费、日志位置和文档命令。路径存在或语法通过不能证明实际分析成功；按 [场景流程](workflows.md)选择验证。

外部原始数据保持只读，不写入、移动、重命名或删除。输出仅写入工作目录；需要复制时核对文件清单、字节数及按风险选择的内容校验。若工具会原地改写“输入副本”的内容、头信息或帧数，另建可写工作副本，保存上游原件和来源。运行后的副本不能充当原始状态；目录整理不自动授权重跑可能改写数据的流程。

## 版本、日期与编码

对一组连贯的实际修改同步更新适用的版本、更新日期和修改记录，无需每次键入递增。同一发布单元有统一元信息时遵守既有机制，文档另有独立版本则保持其记录准确：不兼容变更升主版本，兼容新增升次版本，修复和小改升修订号；重排章节不必自动升主版本。历史版本记录保留其时间和适用范围，不为新规则重写旧记录。

分析文档、阶段记录和审计文档使用下列头部；[阶段模板](workflows.md)同样遵守此要求。例中的版本、日期、作者和说明须替换成实际信息。

```markdown
# {文档标题}

> 版本: v1.0.0
> 更新日期: YYYY-MM-DD

| 版本 | 日期 | 修改说明 | 作者 |
|---|---|---|---|
| v1.0.0 | YYYY-MM-DD | 初版及本次实际范围 | 实际作者 |
```

新增脚本和 Markdown 使用 UTF-8 no BOM，中文无乱码；跨平台默认 LF。已有 Windows PowerShell 文件可按工具要求保留 CRLF，避免仅为换行批量改文件。Python 入口脚本保留 shebang 和 UTF-8 声明；平台启动方式仍需实际验证。

生成或修改文本文件后，运行 `scripts/check_text_health.py`；涉及 `.gitignore` 时加 `--gitignore`。未运行则说明原因与影响。

## 归档与证据

阶段记录归入 `docs/`，审查和审计报告归入 `docs/audit/`，多份时按主题、轮次或版本及日期命名并维护必要索引。审计可保留各轮，或在最终采用版本中汇总并注明来源，不静默改写历史统计或结论。发现历史错误时保留原适用范围，增加说明和待复核项。

跨位置产出以已确定的主工作目录为最终归属；确需外部处理时，在不违背数据存储边界的前提下同步结果或登记稳定引用，记录日期、来源、目标、文件清单与核对结果。原始数据可保留在外部只读位置，不为“归属统一”强行搬动。整理迁移的回退及清理规则见 [整理参考](workspace-organization.md)。

涉及 Git 状态、文件存在、当前版本等会变化的陈述，写明“截至 YYYY-MM-DD/commit”；交付前复核，不把历史状态写成当前状态。

报告区分直接测得、实际运行记录、静态代码声明和推断，写明检查范围。哈希相同只支持对应时点字节相同；日志完成、路径存在、语法检查都不能代替格式、数值及领域 QC。未运行的分析或跨语言检查明确标记未执行，不写成通过。
