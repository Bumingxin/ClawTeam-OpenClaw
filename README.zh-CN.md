<h1 align="center">🦞ClawTeam-OpenClaw</h1>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <strong>面向 CLI 编码 Agent 的多智能体协作框架 —— 默认以 <a href="https://openclaw.ai">OpenClaw</a> 为核心运行时</strong>
</p>

<p align="center">
  <a href="https://github.com/HKUDS/ClawTeam"><img src="https://img.shields.io/badge/upstream-HKUDS%2FClawTeam-purple?style=for-the-badge" alt="Upstream"></a>
  <a href="#-快速开始"><img src="https://img.shields.io/badge/Quick_Start-3_min-blue?style=for-the-badge" alt="Quick Start"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-≥3.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/agents-OpenClaw_%7C_Claude_Code_%7C_Codex_%7C_nanobot-blueviolet" alt="Agents">
  <img src="https://img.shields.io/badge/transport-File_%7C_ZeroMQ_P2P-orange" alt="Transport">
  <img src="https://img.shields.io/badge/version-0.3.7-teal" alt="Version">
</p>

> 这是一个基于 [HKUDS/ClawTeam](https://github.com/HKUDS/ClawTeam) 的分叉版本，针对 **OpenClaw** 做了深度适配：默认 `openclaw` 作为 agent、支持 per-agent session isolation、自动配置 exec approvals，并补充了更适合实际生产使用的 spawn backend 细节。

你只需要给出目标，Agent 团队就可以协作完成：自动拉起 worker、拆分任务、沟通进展、合并结果。

支持 [OpenClaw](https://openclaw.ai)（默认）、[Claude Code](https://claude.ai/claude-code)、[Codex](https://openai.com/codex)、[nanobot](https://github.com/HKUDS/nanobot)、[Cursor](https://cursor.com) 以及其他命令行 Agent。

---

## v0.3.7 更新内容

- `clawteam spawn --task ...` 现在默认会自动创建 task 卡片，Web UI 用户无需再手工执行 `clawteam task create`
- 新增 `--auto-task/--no-auto-task`，使默认建卡行为可显式控制
- 为 `clawteam spawn` 新增初始版 `--model` / `--thinking` 参数入口
- 针对 OpenClaw 后端增加安全保护：当当前 OpenClaw CLI 无法真实支持运行时模型覆盖时，ClawTeam 会**明确报错**，不再伪装为“模型指定成功”
- 将模型信息向 team member / identity / prompt 侧透传，便于未来兼容扩展与调试
- 明确 OpenClaw-first 的产品规则：Web UI 可见 task 卡片属于默认工作流，而不是额外手动步骤

---

## 为什么要用 ClawTeam？

单个 AI Agent 很强，但通常是**孤立工作**的。ClawTeam 的价值在于：

- 把一个复杂目标拆给多个 Agent 并行处理
- 用任务板和收件箱组织协作
- 让 leader 负责调度、汇总和收口
- 用 git worktree + tmux 让每个 Agent 拥有独立工作空间

| 维度 | ClawTeam | 常见多 Agent 框架 |
|---|---|---|
| 谁在使用 | Agent 自己调用 | 人工编排为主 |
| 启动方式 | `pip install` + 一句提示词 | Docker / YAML / 云服务 |
| 基础设施 | 文件系统 + tmux | Redis / MQ / DB |
| Agent 支持 | 任意 CLI Agent | 常常绑定某个框架 |
| 隔离方式 | git worktree | 容器 / 虚拟环境 |

---

## 它是怎么工作的？

### 1. Agent 拉起 Agent
leader 通过 `clawteam spawn` 创建 worker。每个 worker 都有：
- 独立 git worktree
- 独立 tmux 窗口
- 独立身份与上下文

```bash
clawteam spawn --team my-team \
  --agent-name worker1 \
  --task "Implement auth module"
```

### 2. Agent 和 Agent 之间沟通
worker 可以通过任务板和 inbox：
- 查看自己任务
- 汇报完成情况
- 请求帮助
- 向 leader 回传结果

```bash
clawteam task list my-team --owner me
clawteam inbox send my-team leader "Auth done. All tests passing."
```

### 3. 你负责下达目标，系统负责协作
可以通过：
- `clawteam board show` 看任务板
- `clawteam board attach` 看 tmux 平铺视图
- `clawteam board serve --port 8080` 看 Web UI

---

## 🚀 快速开始

### 方式 1：让 Agent 自己驱动（推荐）

安装完之后，直接对你的 Agent 说：

```text
“Build a web app. Use clawteam to split the work across multiple agents.”
```

Agent 会自动：
- 创建 team
- 拆任务
- 拉起 worker
- 协调执行
- 汇总结果

### 方式 2：你手动控制

```bash
# 创建 team
clawteam team spawn-team my-team -d "Build the auth module" -n leader

# 启动两个 worker
clawteam spawn --team my-team --agent-name alice --task "Implement OAuth2 flow"
clawteam spawn --team my-team --agent-name bob   --task "Write unit tests for auth"

# 查看执行情况
clawteam board attach my-team
```

---

## 支持的 Agent

| Agent | 启动方式 | 状态 |
|-------|---------|------|
| OpenClaw | `clawteam spawn tmux openclaw --team ...` | **默认** |
| Claude Code | `clawteam spawn tmux claude --team ...` | 完整支持 |
| Codex | `clawteam spawn tmux codex --team ...` | 完整支持 |
| nanobot | `clawteam spawn tmux nanobot --team ...` | 完整支持 |
| Cursor | `clawteam spawn subprocess cursor --team ...` | 实验性 |
| 自定义脚本 | `clawteam spawn subprocess python --team ...` | 完整支持 |

---

## 安装

### Step 1：前置依赖

需要：
- Python 3.10+
- tmux
- 至少一个 CLI Agent（推荐 OpenClaw）

检查命令：

```bash
python3 --version
tmux -V
openclaw --version
```

### Step 2：安装 ClawTeam

> **注意**：不要用 `pip install clawteam`，那会装到上游 PyPI 版本，而不是这个 OpenClaw 适配分叉版。

```bash
git clone https://github.com/Bumingxin/ClawTeam-OpenClaw.git
cd ClawTeam-OpenClaw
pip install -e .
```

可选（P2P / ZeroMQ 支持）：

```bash
pip install -e ".[p2p]"
```

### Step 3：创建 `~/bin/clawteam` 软链接

```bash
mkdir -p ~/bin
ln -sf "$(which clawteam)" ~/bin/clawteam
```

并确保 `~/bin` 已加入 PATH：

```bash
export PATH="$HOME/bin:$PATH"
```

### Step 4：安装 OpenClaw skill

```bash
mkdir -p ~/.openclaw/workspace/skills/clawteam
cp skills/openclaw/SKILL.md ~/.openclaw/workspace/skills/clawteam/SKILL.md
```

### Step 5：配置 exec approvals

```bash
python3 -c "
import json, pathlib
p = pathlib.Path.home() / '.openclaw' / 'exec-approvals.json'
if p.exists():
    d = json.loads(p.read_text())
    d.setdefault('defaults', {})['security'] = 'allowlist'
    p.write_text(json.dumps(d, indent=2))
    print('exec-approvals.json updated: security = allowlist')
else:
    print('exec-approvals.json not found — run openclaw once first, then re-run this step')
"

openclaw approvals allowlist add --agent "*" "*/clawteam"
```

### Step 6：验证

```bash
clawteam --version
clawteam config health
openclaw skills list | grep clawteam
```

---

## 已验证的 OpenClaw 工作流

该分叉版本已经在真实 OpenClaw 环境中验证通过以下链路：

- **单 worker 执行**：OpenClaw worker 能接任务、执行并向 leader 回传
- **双 worker 并行执行**：两个 worker 可以并行完成不同任务
- **依赖任务解除**：`--blocked-by` 的任务会在上游任务完成后自动从 `blocked` 变成 `pending`
- **leader 自动汇总**：当 leader-owned synthesis task 解锁后，系统可以自动拉起 leader 完成总结与收口

详细验证记录见：
- [`docs/openclaw-validation.md`](./docs/openclaw-validation.md)

## Web UI 默认行为

当前 Web UI 已按 OpenClaw 实战使用习惯调整为：

- 默认监听：`0.0.0.0`
- 默认端口：`8090`
- 默认界面语言：**简体中文**
- 默认定位：局域网可访问的 ClawTeam 指挥中心
- 首页内置多 Team 总看板
- 顶部内置“清理当前 Team”按钮
- 支持当前浏览器本地保存界面设置

启动命令：

```bash
clawteam board serve
```

局域网设备可通过如下地址访问：

```text
http://<你的内网IP>:8090
```

当前浏览器本地可配置项包括：

- 自定义系统标题
- 总看板每行显示团队数量
- 总看板总共显示团队数量

当前总看板还具备这些行为：

- 首页默认停留在总览页，不会因为只剩 1 个 team 自动跳进详情页
- 点击左上角品牌标题可直接返回首页总览
- team 简介、成员角色、任务标题等更多内容已做简体中文显示层翻译

---

## 核心特性

### Agent 自组织
- leader 拉起并管理 worker
- 自动注入协作提示词
- worker 自主汇报状态
- 支持任意 CLI Agent

### 工作区隔离
- 每个 Agent 一个 git worktree
- 避免多人同时改同一目录
- 支持 checkpoint / merge / cleanup

### 带依赖的任务管理
- `pending` → `in_progress` → `completed` / `blocked`
- `--blocked-by` 支持依赖链
- 完成上游任务会自动解锁下游任务

### Agent 间消息通信
- 点对点 inbox
- broadcast 广播
- 文件系统 transport（默认）
- 可选 P2P transport

### 监控与看板
- `board show`：终端 Kanban 看板
- `board live`：自动刷新
- `board attach`：tmux 平铺观察所有 agent
- `board serve`：Web UI

---

## OpenClaw 集成价值

这个分叉的核心意义在于：

> **把原本单点工作的 OpenClaw，升级成可组织、多角色、可依赖、可并行的多 Agent 协作平台。**

在没有 ClawTeam 时，OpenClaw 更多是“单体执行”。
加上 ClawTeam 后，可以实现：

- leader 自动拆任务
- worker 并行工作
- inbox 回执链路
- 依赖任务自动解锁
- leader 自动汇总结果

---

## 命令示例

### Team 生命周期

```bash
clawteam team spawn-team <team> -d "description" -n <leader>
clawteam team discover
clawteam team status <team>
clawteam team cleanup <team> --force
```

### Spawn Agent

```bash
clawteam spawn --team <team> --agent-name <name> --task "do this"
```

### 任务管理

```bash
clawteam task create <team> "subject" -o <owner> --blocked-by <id1>,<id2>
clawteam task update <team> <id> --status completed
clawteam task list <team>
clawteam task wait <team> --timeout 300
clawteam task wait <team> --final-report --reporter reviewer --takeover
```

### 消息

```bash
clawteam inbox send <team> <to> "message"
clawteam inbox broadcast <team> "message"
clawteam inbox receive <team>
clawteam inbox peek <team>
```

### 看板与观察

```bash
clawteam board show <team>
clawteam board live <team> --interval 3
clawteam board attach <team>
clawteam board serve --port 8090
```

---

## 路线图（简版）

| 版本 | 内容 | 状态 |
|------|------|------|
| v0.3 | File + P2P transport、Web UI、多用户、模板 | 已发布 |
| v0.4 | Redis transport / 跨机消息 | 计划中 |
| v0.5 | 更强的共享状态层 | 计划中 |
| v0.6 | Agent 模板市场 | 探索中 |
| v0.7 | 自适应调度 | 探索中 |
| v1.0 | 生产级：权限、审计、稳定性 | 目标 |

---

## License

MIT — 可自由使用、修改、分发。

---

<div align="center">

**ClawTeam** — *Agent Swarm Intelligence.*

</div>
