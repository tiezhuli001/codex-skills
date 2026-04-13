# codex-skills

面向执行型 agent 工作流的一组实用 Codex skills。

> 核心目标不是“写得像 prompt”，而是让 Codex 在真实任务里更能干活：清理仓库、持续执行、验证优先、少废话、少污染。

[English](./README.md) · [贡献说明](./CONTRIBUTING.md)

## 这个仓库是什么

`codex-skills` 是一个小而聚焦的多-skill 仓库，专门收纳那些能真正改善 Codex 执行行为的 skill。

它不是一堆零散 prompt，而是可复用、可维护、可在不同仓库里持续使用的执行规则集合。

它主要解决这类问题：
- AI / agent 仓库不断膨胀，却很难安全瘦身
- 长任务容易停在分析、handoff、总结，而不是继续推进
- 工具和中间产物污染用户仓库
- 同类任务每次都要重新写 prompt，行为不稳定

## 适合谁用

适合这些人：
- 把 Codex 当执行 agent 来用
- 希望 agent 输出更少废话、更多可执行结果
- 希望把好用的 skill 沉淀下来，而不是每次临时拼 prompt
- 希望 skill 能跨仓库复用，并且保持仓库卫生

## 当前包含的 skill

### `ai-repo-cleanup`
一个面向“删除价值”的仓库瘦身 skill，主要适用于 AI / agent 仓库。

适合发现：
- 可疑死代码
- 假活测试
- 弱 helper / support split
- 冗余支持层
- 不该继续污染主仓库的 archive / docs 噪音

它和普通 code review 的区别：
- 目标是 **safe deletion value**，不是泛泛代码审查
- 输出是 **execution package**，不是空泛审计报告
- 如果本轮没有真正可动的清理项，会自动压缩成 **zero-action mode**
- 默认要求工具中间产物外置
- 明确禁止 GitNexus 一类工具污染仓库 instruction files，例如 `AGENTS.md` / `CLAUDE.md`

### `long-run-execution`
一个面向长流程持续执行的 skill，避免 Codex 在任务中途滑向：
- 分析停顿
- handoff
- 中途总结
- “下一个 agent 可以继续”

适合用户明确表达这类意图时使用：
- 一直做下去
- 做到下一个已验证里程碑
- 不要中途停下来讲计划
- 每一小步做完就验证

它的核心特点：
- 把每个 slice 锁定在 target / boundary / proof
- 把 verification 变成执行节奏的一部分
- 把 handoff-as-substitute-for-work 当成失败
- continuity 保持短、小、贴近现实

## 典型使用场景

### 示例 1：仓库瘦身
用户说：

```text
Use ai-repo-cleanup to audit this repo and generate a cleanup list.
```

理想输出：
- 先给出 delete-ready / high-probability 项
- 中间工具产物不污染仓库
- 编码 agent 能直接按清单执行

### 示例 2：长任务持续执行
用户说：

```text
Keep going until this feature is implemented and verified.
```

理想输出：
- 不停在中途总结
- 每个 slice 都有验证
- continuity 反映真实进度，而不是空泛 handoff

## 设计原则

这个仓库偏好这样的 skill：
- **execution first**
- **verification before claims**
- **范围小，但规则硬**
- **跨仓库复用**
- **重视仓库卫生**

明确的非目标：
- 不做一个很重的 skill framework
- 不把所有个人 prompt 都堆进来开源
- 不为了“像产品”而增加很多不必要的包装层

## 安装方式

### 安装全部 skill

```bash
cd codex-skills
./scripts/install.sh
```

### 只安装一个 skill

```bash
cd codex-skills
./scripts/install.sh ai-repo-cleanup
```

### 安装到自定义 Codex 目录

```bash
CODEX_HOME=/path/to/custom/codex ./scripts/install.sh
```

默认安装目标：

```bash
$HOME/.codex/skills
```

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

如果你不想覆盖真实的 Codex 环境，可以这样测试：

```bash
CODEX_HOME=$PWD/.tmp/codex-home ./scripts/install.sh ai-repo-cleanup
```

## 路线图

后续可能会加入：
- 同一工作流家族里的更多 execution-oriented skills
- 更完整的 skill 使用示例与前后对比
- 更清晰的 skill 版本变更说明

但仓库会继续保持小而聚焦。

## License

MIT
