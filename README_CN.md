# codex-skills

一组适合开源的 Codex 技能仓库，面向 agent 执行工作流。

当前包含：
- `ai-repo-cleanup`：面向删除的仓库瘦身审计 skill
- `long-run-execution`：面向长流程持续执行、避免中途 handoff 漂移的 skill

## 为什么放在一个仓库

这个仓库采用 **一个项目，多个 skill** 的组织方式。

这样做的好处：
- skill 可以各自独立演进
- 但共享安装方式
- 共享文档规范
- 共享版本管理与开源说明
- 用户安装和发现成本更低

## 仓库结构

```text
codex-skills/
  README.md
  README_CN.md
  LICENSE
  scripts/
    install.sh
  skills/
    ai-repo-cleanup/
      SKILL.md
      references/
      scripts/
    long-run-execution/
      SKILL.md
```

## 快速安装

安装仓库内全部 skill：

```bash
cd codex-skills
./scripts/install.sh
```

只安装一个 skill：

```bash
cd codex-skills
./scripts/install.sh ai-repo-cleanup
```

默认安装到：

```bash
$HOME/.codex/skills
```

如果你想改安装目标，可以覆盖 `CODEX_HOME`：

```bash
CODEX_HOME=/path/to/custom/codex ./scripts/install.sh
```

## 包含的 skill

### `ai-repo-cleanup`
适用于 AI / agent 仓库瘦身，核心目标是找出：
- 可删除代码
- 假活测试
- 弱 helper / support split
- 冗余支持层
- 不应继续污染主仓库的 archive / docs 噪音

### `long-run-execution`
适用于用户明确希望 agent 持续推进、持续验证、不要中途停在分析/计划/handoff 的场景。

## 开发方式

修改 skill 时，直接编辑：

```bash
skills/<skill-name>/
```

修改后本地重新安装：

```bash
./scripts/install.sh
```

## License

MIT
