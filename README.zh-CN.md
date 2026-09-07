# Vank

Vank 是一套 gstack 式 skill 包：**一个 git 仓库、一次安装、多个子技能**。

根目录 [`SKILL.md`](SKILL.md) 只做路由。真正的工作流在嵌套的 `vk-*` 目录里（问答、读代码、roadmap、需求 DSL、后端门禁、实现、评审、提交、写作、iOS、流程图、飞书、技能治理）。

- 中文：本文件
- English: [README.md](README.md)

## 目录结构

```text
vank/
  SKILL.md                 # 路由器（$vank）
  shared/vk-core-contract.md
  vk-question/ ...         # 子技能
  scripts/install.sh
  README.md
  README.zh-CN.md
```

子技能的 `name:` 仍是 `vk-*`，所以 `$vk-work` 继续有效。`$vank` 只负责路由；`$vk-work` 才执行。

说明文档与技能正文使用英文。面向用户的自然语言结果默认跟随用户语言。

## 安装

在本仓库根目录执行：

```bash
bash scripts/install.sh
```

该命令会：

1. 把本仓库软链到 `~/.codex/skills/vank`、`~/.claude/skills/vank`、`~/.cursor/skills/vank`
2. 让子技能留在包内，由宿主像发现 gstack 那样递归发现
3. 清掉宿主根上指向本仓库的散装 `vk-*` 链接
4. 若存在 `vk-submit/scripts/vkpush`，则固定到 `~/.local/bin/vkpush`

演练：

```bash
bash scripts/install.sh --dry-run
```

若宿主不会递归扫描嵌套 `SKILL.md`，安装后可能只看得到 `$vank`、看不到 `$vk-work`。请再跑：

```bash
bash scripts/install.sh --with-shims
```

卸载软链（不删除本 git 仓库）：

```bash
bash scripts/uninstall.sh
```

可选环境变量：`CODEX_SKILLS_DIR`、`CLAUDE_SKILLS_DIR`、`CURSOR_SKILLS_DIR`、`AGENTS_SKILLS_DIR`、`LOCAL_BIN_DIR`。

安装后请 **新开一个会话**，宿主才会重新加载技能。

## 用法

| 你怎么说 | 实际跑什么 |
| --- | --- |
| `$vank` / 「用 vank」 | 路由器选一个子技能，然后完整执行该子技能的 `SKILL.md` |
| `$vk-work`、`$vk-request` … | 直接进命名子技能，跳过路由 |
| Claude Code 里的 `/vk-review` | 等同 `$vk-review` |

不要用路由表顶替子技能正文。

常见顺序（已完成的阶段直接跳过）：

```text
question / read / roadmap → request → restrict → work → review → submit
```

专项技能（`vk-writer`、`vk-ios-agents`、`vk-diagram-guard`、`vk-write-lark`）只在对应领域出现时加载。

### 可选的 gstack 交付门禁

`vk-work` 仍是总控。本地验证之后，仅当专项能力真正匹配时才读
[Vank–gstack 交付桥接规则](references/gstack-bridge.md)：有页面时的浏览器验收、用户要求的额外安全审查、或已授权的发布。后端容量测试留在 Vank。日常提交只走 `vk-submit`。gstack `qa` 不得提交。

### 子技能

| 技能 | 适用 |
| --- | --- |
| `vk-question` | 概念、取舍、问答 |
| `vk-read` | 只读追踪代码 |
| `vk-roadmap` | 仓库 / 模块地图 |
| `vk-request` | 意图 → 可执行 DSL |
| `vk-restrict` | 后端数据流 / IO / 依赖门禁 |
| `vk-work` | 实现、修复、长任务交付 |
| `vk-review` | diff 审查与风险 |
| `vk-submit` | 提交、推送、`vkpush` |
| `vk-writer` | 长文成套资产 |
| `vk-ios-agents` | iOS 多技能编排 |
| `vk-diagram-guard` | 流程图门禁与修复 |
| `vk-write-lark` | 本地文档 → 飞书计划（有工具且目标明确才真写） |
| `vk-skill-man` | 维护本包 / 本地 skill 卫生 |

## 本地记录

只有重要的技能执行记录才写在 **目标项目** 里，不写进本包；Vank 不会因为技能运行过就自动建档：

- `./vk/<skill-key>/`（例如 `vk-work` → `./vk/work/`）
- 长任务恢复：只维护一份 `./vk/work/checkpoint.md`，就地更新
- 目标项目 `.gitignore` 忽略 `vk/`
- 记录跨模块决策、风险、可复用方案、交接、阻塞和用户明确要求保留的内容；普通问答、状态确认、短暂阅读和已验证的小改动默认不记录。
- roadmap、DSL、文章等用户直接要求的文件仍会照常生成，它们不是额外的执行记录。

可选、可提交的产品上下文：`./vank/context|specs|decisions/`。不要在那里再写一份「当前状态」。见 [references/contract.md](references/contract.md)。

## 本包维护

日常卫生：`$vk-skill-man`。形态与安装策略：[references/governance.md](references/governance.md)。
