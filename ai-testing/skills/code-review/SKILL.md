---
name: code-review
description: 对代码变更执行四维度审查（Bug/安全/性能/可维护性），生成结构化报告并给出 QA 测试范围建议。触发场景：用户提供 git diff、PR URL、分支名，或要求审查当前代码变更时。
---

# 代码审查

## Step 1：获取代码变更

> 执行场景：QA 本地已克隆仓库，对研发推送的代码进行审查（非开发者自测）。

先同步远端最新代码：
```bash
git fetch origin
```

如果用户已在命令中提供变更来源，直接使用。否则询问：

> "请提供研发的代码变更来源：
> 1. 特性分支名（研发已推送的分支，如 feature-xxx 或 fix-yyy）
> 2. PR/MR URL（如 https://github.com/owner/repo/pull/123）
> 3. 提交区间（如 abc123..def456，对应某次迭代范围）
> 4. 最近 N 次提交（请提供 N）"

根据来源获取 diff：

```bash
# 选项1：特性分支与主干对比
git diff main...origin/<branch-name>

# 选项2：PR（使用 gh CLI，从 URL 提取 PR 号）
gh pr diff <pr-number>

# 选项3：指定提交区间
git diff <commitA>..<commitB>

# 选项4：最近 N 次提交
git diff HEAD~N..HEAD
```

同时获取变更文件列表：
```bash
# 对应替换 <range> 为上面实际使用的范围
git diff --name-only <range>
```

如果 diff 为空，告知"未检测到代码变更"并退出。

## Step 2：推断项目类型

```bash
ls -la
```
根据文件（package.json → TypeScript/JavaScript，pom.xml → Java，go.mod → Go，requirements.txt → Python）推断项目类型。

## Step 3：执行审查

启动 `code-reviewer` subagent，传入：
- diff 内容（完整文本）
- 项目类型（推断结果）
- 变更文件列表

## Step 4：保存产物

将 subagent 输出的完整报告内容写入 `reports/code-review.md`（如 reports/ 目录不存在，先创建）。

读取 `reports/artifacts.json`（不存在则初始化为 `{}`），添加或更新键值：
```json
{ "code-review": "reports/code-review.md" }
```
写回 `reports/artifacts.json`。

## Step 5：告知用户

输出：
- 报告已保存到：`reports/code-review.md`
- 发现问题：CRITICAL(N) HIGH(N) MEDIUM(N) LOW(N)
- 建议下一步：执行 `/ai-testing:gen-test-cases` 生成测试用例
