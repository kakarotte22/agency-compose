# Agency Compose —— 一句话多智能体编排（Claude Code 原生版）

将 `agency-orchestrator` 的「一句话编排多智能体」能力改造为 **Claude Code 原生**实现：

- 286 个专家角色 → 286 个 **subagent**（`.claude/agents/`）
- 一句话编排 → **`/compose`** 斜杠命令（`.claude/commands/compose.md`）

改造后的项目完全脱离 `agency-orchestrator` 运行时，由 Claude Code 原生调度。

---

## 目录结构

```
agency-compose/
├── .claude/
│   ├── agent-manifest.json     # 286 个角色的目录清单（供编排时检索）
│   ├── agents/                 # 286 个 subagent 定义
│   │   ├── engineering/
│   │   │   └── engineering-code-reviewer.md
│   │   ├── product/
│   │   ├── marketing/
│   │   └── ...（20 个部门分类）
│   └── commands/
│       └── compose.md          # /compose 斜杠命令
├── cases/                      # 每次任务的存档：DAG方案/步骤产出/代码与结果/最终报告
│   └── <任务名>-时间戳/
│       ├── 00-总览.md          # 阅读锚点（DAG图 + 结论 + 导航表）
│       ├── 10-DAG方案.json
│       ├── 20-执行日志.md
│       ├── 30-步骤产出/
│       ├── 40-代码与结果/
│       └── 50-最终报告.md
└── README.md
```

---

## 使用方法

1. 启动 Claude Code 时，**把本项目文件夹设为工作目录**：

   ```bash
   cd ~/Desktop/agency-compose
   claude
   ```

2. 输入斜杠命令 + 一句话需求：

   ```
   /compose 帮我写一篇关于多智能体协作的深度分析文章
   ```

3. Claude Code 会自动：
   - 调 `engineering-multi-agent-systems-architect`（多智能体架构师）设计编排方案（DAG，含带轮次上限的循环）
   - 主程序按方案用 `Agent` 工具真实调度多个 subagent 串行/并行执行
   - 汇总裁决出最终成品
   - 把全程过程数据存档到 `cases/<任务名>-时间戳/`，供事后 review

---

## 工作原理

`/compose` 采用「**架构师设计 → 主程序执行**」的两步模式：

1. **设计**：主程序读 `agent-manifest.json` 拿到角色清单，再调起 `engineering-multi-agent-systems-architect`，由它产出结构化编排方案（拓扑 + steps + 循环的 `max_rounds`/`converge_when` + `missing_roles`）。架构师只设计、不执行。
2. **执行**：主程序按方案真实调度角色——无依赖的并发、有依赖的串行、循环按设计好的上限强制收敛——最后按 `merge` 策略汇总成品。主程序只执行、不设计。

对比原 `agency-orchestrator`：

| AO 概念 | 本项目的 Claude Code 原生对等物 |
|---------|-------------------------------|
| 角色 `.md`（frontmatter + SOP） | subagent 定义（`.claude/agents/*.md`） |
| 编排 YAML（DAG 依赖） | 架构师产出的结构化方案 → 主程序用 `Agent` 调度 |
| `compose` 一句话生成 workflow | `/compose <一句话>` 斜杠命令 |
| 并行执行（`concurrency`） | 同一条消息发多个 `Agent` 调用并发执行 |
| 变量传递（`{{var}}`） | 上游 Agent 返回结果 → 下游 Agent 的 prompt |
| 反思/校验/收敛（元角色） | 已移除；架构师在 DAG 里内嵌带轮次上限的辩论循环 |

---

## 角色清单

286 个角色按部门分布在 `.claude/agents/` 下，完整清单见 `.claude/agent-manifest.json`。

每个 subagent 的 `name` 字段（英文 slug）就是调度时的 `subagent_type`，中文名在 `cn_name` 字段。

快速查看可用角色个数：

```bash
find .claude/agents -name '*.md' | wc -l   # 286
```

---

## 与原项目的差异

| 维度 | agency-orchestrator | 本项目 |
|------|--------------------|--------|
| 运行引擎 | AO 自己的 DAG 执行器 | Claude Code 原生 Agent 调度 |
| 角色格式 | `agency-agents-zh/*.md` | Claude Code subagent 格式 |
| 关键区别 | YAML 需要 AO 解析，Claude Code 不认 | subagent 是 Claude Code 一等公民 |
| 依赖 | 需安装 ao 命令 | 无需额外安装，纯文件 |

---

## 二次扩展

- **加自建角色**：在 `.claude/agents/` 下新建部门子目录，按 subagent 格式写 `.md`，再把它登记进 `agent-manifest.json`
- **改编排逻辑**：直接编辑 `.claude/commands/compose.md`（设计/执行/异常处理/运行留痕各节）
- **调留痕机制**：编辑 compose.md 第 5 节「运行留痕」的目录约定
- **换个命令名**：把 `compose.md` 重命名为你想要的名字，斜杠命令会自动改名
