# codex-skills

<div align="center">

一组面向执行型工作流的 Codex skills，聚焦仓库瘦身、长流程持续执行、低噪音验证推进。

[English](./README.md) · [贡献说明](./CONTRIBUTING.md) · [ai-repo-cleanup](./skills/ai-repo-cleanup/README.md) · [long-run-execution](./skills/long-run-execution/README.md)

![Skills](https://img.shields.io/badge/skills-2-black?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Focus](https://img.shields.io/badge/focus-execution--first-blue?style=flat-square)

</div>

`codex-skills` 是一个小而聚焦的开源仓库，核心目标很窄：让 Codex 在真实执行任务里更稳定、更可复用、更少废话。

当前中心重心是：

`repo cleanup -> verified execution -> low-noise continuity`

如果一个 skill 不能帮助 Codex 产出更清晰的执行结果、更安全的清理动作或更强的验证闭环，它大概率就不该放进这个仓库。

## Overview

- execution-first 的 Codex skills
- verification before claims
- 默认重视仓库卫生
- 低噪音输出，避免分析表演
- 一个仓库，多个聚焦 skill

## 为什么有这个仓库

很多 prompt 集合看起来很多，但难复用、难维护，而且一旦进入真实任务就容易变软。`codex-skills` 刻意更窄。

它只关注那些能真实改善执行行为的 skill，例如：
- 在不破坏活跃合同的前提下瘦身 AI 生成仓库
- 让长任务沿着已验证 slice 持续推进，而不是滑向 handoff 表演
- 防止工具和中间产物污染用户仓库
- 把可重复的执行模式沉淀成 skill，而不是每次重写 prompt

## 一眼看懂

| Skill | 作用 |
| --- | --- |
| `ai-repo-cleanup` | 为 AI / agent 仓库找到真正值得删除或退休的清理项 |
| `long-run-execution` | 让 Codex 一直执行到下一个真实里程碑，而不是中途停在总结 |

## 当前包含的 Skill

### `ai-repo-cleanup`
一个面向“删除价值”的仓库瘦身 skill，主要用于 AI / agent 代码库。

最适合处理：
- 可疑死代码
- 假活测试
- 弱 helper / support split
- 冗余支持层
- 不该继续压过主仓库的 docs / history 噪音

核心特点：
- 优先优化 **safe deletion value**，不是泛泛 code review
- 输出是 **execution package**，不是空泛审计报告
- 当本轮没有真正可动项时，支持 **zero-action compression**
- 默认要求工具产物外置
- 明确禁止 GitNexus 一类工具污染仓库 instruction files，例如 `AGENTS.md` / `CLAUDE.md`

### `long-run-execution`
一个用于长流程持续执行的 skill，避免 Codex 在任务中途滑向中途总结或假 handoff。

最适合处理：
- 持续执行
- 每个 slice 后立即验证
- 一直推进到下一个真实里程碑
- 降低“下一个 agent 可以继续”式漂移

核心特点：
- 每个 slice 都锁定 target / boundary / proof
- 把 verification 变成执行节奏的一部分
- 把 handoff-as-substitute-for-work 当成失败
- continuity 保持短、小、贴近现实

## 典型使用场景

### 仓库瘦身

```text
Use ai-repo-cleanup to audit this repo and generate a cleanup list.
```

理想输出：
- 先给出 delete-ready / high-probability 项
- 工具产物不污染仓库
- 编码 agent 可以直接执行结果

### 长任务持续执行

```text
Keep going until this feature is implemented and verified.
```

理想输出：
- 不停在中途总结
- 每个 slice 都有验证
- continuity 反映真实进度，而不是空泛 handoff

## 设计原则

`codex-skills` 偏好这样的 skill：
- **execution-first**
- **verification-driven**
- **范围小，但规则硬**
- **可跨仓库复用**
- **重视仓库卫生**

明确非目标：
- 不做一个很重的 skill framework
- 不把所有个人 prompt 都堆进来开源
- 不为了“像产品”而增加很多不必要的包装层

## 仓库结构

```text
codex-skills/
  README.md
  README_CN.md
  CONTRIBUTING.md
  LICENSE
  scripts/
    install.sh
  skills/
    ai-repo-cleanup/
      README.md
      SKILL.md
      references/
      scripts/
    long-run-execution/
      README.md
      SKILL.md
      long-run-review-template.md
```

## 快速安装

安装全部 skill：

```bash
cd codex-skills
./scripts/install.sh
```

只安装一个 skill：

```bash
cd codex-skills
./scripts/install.sh ai-repo-cleanup
```

安装到自定义 Codex 目录：

```bash
CODEX_HOME=/path/to/custom/codex ./scripts/install.sh
```

默认安装目标：

```bash
$HOME/.codex/skills
```

## 开发方式

直接修改：

```bash
skills/<skill-name>/
```

修改后本地重新安装：

```bash
./scripts/install.sh
```

如果不想覆盖真实 Codex 环境，可以这样测试：

```bash
CODEX_HOME=$PWD/.tmp/codex-home ./scripts/install.sh ai-repo-cleanup
```

## 路线图

后续可能加入：
- 同一工作流家族里的更多 execution-oriented skills
- 更完整的示例与前后对比
- 更轻量的行为变更说明

但仓库会继续保持小而聚焦。

## License

MIT
