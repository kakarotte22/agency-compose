# Agency Compose —— 一句话多智能体编排（Claude Code 原生版）

将 `agency-orchestrator` 的「一句话编排多智能体」能力改造为 **Claude Code 原生**实现：

- 334 个专家角色 → 334 个 **subagent**（`.claude/agents/`，以 `agent-manifest.json` 实测为准）
- 一句话编排 → **`/compose`** 斜杠命令（`.claude/commands/compose.md`）

改造后的项目完全脱离 `agency-orchestrator` 运行时，由 Claude Code 原生调度。

> **关于 `cases/` 存档**：`cases/` 是每次 `/compose` 运行的**本地留痕目录**，已通过 `.gitignore` 排除在版本库之外（仅 `.claude/` 里的角色、命令、脚本、以及 `viewer/` 源码入库）。你机器上跑出来的案例只存在本地、不入 git；`viewer/` 依赖它做历史回放，但不会提交这些内容。

---

## 目录结构

```
agency-compose/
├── .claude/
│   ├── agent-manifest.json     # 334 个角色的目录清单（供编排时检索）
│   ├── agent-index.md          # 按任务职能预分组的角色索引（compose 选角用）
│   ├── agents/                 # 334 个 subagent 定义
│   │   ├── engineering/
│   │   │   └── engineering-code-reviewer.md
│   │   ├── product/
│   │   ├── marketing/
│   │   └── ...（20 个部门分类）
│   ├── commands/
│   │   └── compose.md          # /compose 斜杠命令
│   └── scripts/
│       └── check-agent-index.py # 索引与 manifest 一致性自检
├── viewer/                     # 本地可视化 + Web 编排工作台（见下文）
│   ├── server.py               # 本地服务（标准库，零依赖）
│   ├── parse_case.py           # case 目录 → 结构化 JSON
│   ├── runner.py               # 拉起 claude CLI 真实执行编排
│   └── index.html              # 自包含前端（DAG + 实时日志）
├── cases/                      # 每次任务的存档：DAG方案/步骤产出/代码与结果/最终报告（已 gitignore，仅存本地）
│   └── <任务名>-时间戳/
│       ├── 00-总览.md          # 阅读锚点（DAG图 + 结论 + 导航表）
│       ├── 10-DAG方案.json
│       ├── 20-执行日志.md
│       ├── 30-步骤产出/
│       ├── 40-代码与结果/
│       ├── 50-最终报告.md
│       └── 90-遗留与偏差.md
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
   - 调 `engineering-multi-agent-systems-architect`（多智能体架构师）设计编排方案（有向图，允许含带轮次上限的回路：回退 / 辩论 / 自迭代）
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

### 可视化查看器

`/compose` 跑完任务后，除了看 `cases/` 里的 markdown，还可以用一个**交互式网页**直观查看任务流图——点击任意节点看它的「输入 prompt」和「输出产出」。

**启动**（Python 标准库，零第三方依赖）：

```bash
python3 viewer/server.py          # 默认端口 8765
python3 viewer/server.py 8080     # 或指定端口
```

浏览器打开 **http://127.0.0.1:8765**。

**能看到什么**：

- **左侧栏**：`cases/` 下所有历史任务，点击切换
- **中间 DAG 图**：分层拓扑布局的任务流，节点=步骤（角色中文名 + 角色 id + 步骤序号），边=依赖；并行 fan-out/fan-in 一目了然，辩论循环节点带 `↻` 徽章
- **点击节点**：右侧滑出详情面板，展示输入 prompt（可复制）、输出契约、关键结论、兜底策略，以及实际产出（markdown 渲染）
- **hover 节点**：高亮其上下游依赖路径
- **顶部 KPI**：总步骤 / 成功 / 失败 / 循环数

**实现文件**：

- `viewer/server.py` —— 本地服务，动态扫描 `cases/` 解析
- `viewer/parse_case.py` —— 把 case 目录解析成结构化数据
- `viewer/index.html` —— 自包含前端（自绘 SVG DAG + 轻量 markdown 渲染）

---

## 角色清单

334 个角色按部门分布在 `.claude/agents/` 下，完整清单见 `.claude/agent-manifest.json`。

每个 subagent 的 `name` 字段（英文 slug）就是调度时的 `subagent_type`，中文名在 `cn_name` 字段。

快速查看可用角色个数：

```bash
find .claude/agents -name '*.md' | wc -l   # 334
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
