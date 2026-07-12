# Codex Skills

用于实现最小化、可追踪、可验证软件交付的可复用 Codex Skills。

## 安装方式

独立安装 Skill 是编写、查看和使用 Codex Skill 最简单的方式，因此默认推荐这种方式。Plugin 并没有替代 Skill 格式；它只是把 `vibecoding-guidance`、`coding-standards` 以及所需的 Superpowers Skill 依赖打包成一个可安装单元。

| 方式 | 适用场景 | 依赖处理 |
| --- | --- | --- |
| 独立 Skill **（推荐）** | 简单安装、直接开发 Skill，或者只使用自己需要的 Skill | 只安装从仓库中选择的 Skill |
| Plugin | 使用完整的 `vibecoding-guidance` 工作流，同时不想逐个安装依赖 | 同时安装仓库 Skill 和锁定版本的 Superpowers 依赖集合 |

### 独立安装 Skill（推荐）

当前 Codex CLI 没有提供 `codex skill add` 子命令。请通过 Codex 内置的 `$skill-installer` 安装，并在命令中指定仓库地址：

```powershell
codex 'Use $skill-installer to install skills/coding-standards and skills/vibecoding-guidance from https://github.com/Euphoria-zy/codex-skills'
```

如果只需要安装不依赖其他 Skill 的 `coding-standards`：

```powershell
codex 'Use $skill-installer to install skills/coding-standards from https://github.com/Euphoria-zy/codex-skills'
```

独立安装的 Skill 使用短名称调用：

```text
$coding-standards Review this change and keep the solution minimal and verifiable.
```

```text
$vibecoding-guidance Turn this product idea into approved, tracked, and verified software delivery.
```

`coding-standards` 可以独立运行。单独安装 `vibecoding-guidance` 时不会自动安装它所需的 Superpowers 依赖；如需完整工作流，可以自行安装这些依赖，或者直接使用 Plugin。

### 安装 Plugin（依赖打包）

先把这个 GitHub 仓库添加为 Codex Plugin Marketplace，再安装已经打包好的 Plugin：

```powershell
codex plugin marketplace add Euphoria-zy/codex-skills --ref main
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

Plugin 中的 Skill 使用 Marketplace 命名空间调用：

```text
$vibecoding-guidance:coding-standards Review this change and keep the solution minimal and verifiable.
```

```text
$vibecoding-guidance:vibecoding-guidance Turn this product idea into approved, tracked, and verified software delivery.
```

更新已经安装的 Plugin：

```powershell
codex plugin marketplace upgrade euphoria-zy-codex-skills
codex plugin add vibecoding-guidance@euphoria-zy-codex-skills
```

无论选择哪种安装方式，安装完成后都建议新建一个 Codex 任务，以便加载新安装的 Skill。

## 仓库包含的源 Skill

| Skill | 用途 |
| --- | --- |
| [`coding-standards`](skills/coding-standards) | 让代码修改保持最小、直接并且可以验证。 |
| [`vibecoding-guidance`](skills/vibecoding-guidance) | 从产品意图到发布全过程，引导经过确认、可追踪、可验证的软件交付。 |

## Plugin 内置依赖

`coding-standards` 本身不依赖其他 Skill。

Plugin 根据 MIT License 打包了以下锁定版本的 Superpowers Skills：

- `superpowers:brainstorming`
- `superpowers:writing-plans`
- `superpowers:test-driven-development`
- `superpowers:systematic-debugging`
- `superpowers:verification-before-completion`
- `superpowers:using-git-worktrees`
- `superpowers:subagent-driven-development`
- `superpowers:executing-plans`
- `superpowers:finishing-a-development-branch`
- `superpowers:requesting-code-review`

在 Plugin 内部，这些依赖引用会被重写到 `vibecoding-guidance:` 命名空间。上游仓库和固定 Commit 记录在 [`dependency-lock.json`](plugins/vibecoding-guidance/dependency-lock.json) 中，完整的上游许可证保存在 [`THIRD_PARTY_NOTICES.md`](plugins/vibecoding-guidance/skills/.third-party/THIRD_PARTY_NOTICES.md) 中。

## Plugin 维护

修改源 Skill 或依赖锁后，执行：

```powershell
python -m unittest discover -s tests -v
python scripts/build_plugin.py --repo-root . --install
python scripts/build_plugin.py --repo-root . --check
python scripts/check_plugin_dependencies.py --repo-root .
python C:/Users/29787/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/vibecoding-guidance
```

不要直接修改 `plugins/vibecoding-guidance/skills/` 下的生成文件。依赖锁或生成内容发生变化时，必须同步提升 Plugin 版本。

## 许可证

本项目采用 [MIT License](LICENSE) 发布。
