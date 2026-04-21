---
name: bug-report
description: 解析多格式 Bug 文件（PDF/Excel/Markdown/Word）和 Playwright 失败结果，Dry-run 确认后批量上报到 JIRA，自动上传截图附件。触发场景：用户要求上报 Bug、提供 Bug 文件，或测试执行完成后。
---

# Bug 上报

## Step 1：收集输入

**自动检测** `reports/playwright-results.json`（如存在，自动使用）。

询问手工文件（可跳过）：
> "是否有手工测试记录的 Bug 文件？支持 PDF/Excel/Markdown/Word（无则直接回复'无'）"

JIRA 项目 Key 默认使用 `WITAKE`，除非用户明确指定其他 Key。

如两个来源都没有，告知"无 Bug 数据来源"并退出。

## Step 2：启动 bug-analyzer

启动 `bug-analyzer` subagent，传入：
- `manual_files`：手工文件路径列表（无则传 []）
- `playwright_results`：`reports/playwright-results.json`（不存在则传空字符串）

等待 subagent 返回标准化 Bug 列表。

**错误处理：**
- subagent 返回错误或异常：告知用户"无法解析文件，错误原因：`<reason>`"，退出
- subagent 返回空列表：告知用户"未在提供的文件中发现 Bug 记录"，退出

## Step 3：确认经办人

检查是否已知经办人（来自上下文或用户之前提供）：
- **已知**：直接使用，无需询问
- **未知**：询问一次：
  > "请输入经办人账号（如 zhangsan 或 zhangsan@rd.netease.com），留空则不指派"

将经办人记录为 `assignee`，空则为 `""`。

## Step 4：Dry-run 预览

将 Bug 列表格式化展示给用户：

```
📋 待上报 Bug 列表（共 N 条）经办人：<assignee 或 '未指派'>

[CRITICAL] 登录按钮点击后页面无响应
  步骤：1. 输入正确账号密码 2. 点击登录
  期望：跳转首页  实际：TypeError 报错
  截图：reports/screenshots/login-fail.png

[HIGH] 搜索框输入特殊字符导致 500 错误
  ...

⚠️ 疑似重复（请确认）：
  - "搜索无结果" 与 "搜索返回空列表" 描述相似

确认上报哪些？（全部确认/输入要跳过的序号，如 '跳过 3,5'）
```

解析"跳过"列表时：
- 忽略超出范围的序号（提示 warn）
- 容忍空格变体（"跳过 3, 5" 与 "跳过3,5" 等效）
- 如输入无法解析，重新询问用户

根据用户回复，确定最终上报列表。

## Step 5：批量上报 JIRA

对每条确认上报的 Bug，调用 `mcp__mcp-atlassian__jira_create_issue`：

```
project_key: <用户提供的 Key，默认 WITAKE>
summary: <bug.title>（含关键上下文，如页面名称、错误现象）
issue_type: "开发 Bug"
assignee: <assignee>（非空时传入）
additional_fields: '{
  "priority": {"name": "<severity_map>"},
  "customfield_10406": "【测试环境】\n<env>\n\n【前提条件】\n<preconditions>\n\n【测试步骤】\n<steps>\n\n【预期结果】\n<expected>\n\n【实际结果】\n<actual>"
}'
```

注意：WITAKE 项目标准 `description` 字段不在可编辑 screen 上，**改用 `customfield_10406`（bug 描述）填写详情**。

severity 映射：CRITICAL→Highest，HIGH→High，MEDIUM→Medium，LOW→Low

如有截图（`bug.screenshot` 非空），先执行：
```bash
ls "<screenshot_path>" 2>/dev/null
```
**文件存在**时上传附件：
```
mcp__mcp-atlassian__jira_update_issue(
  issue_key = <创建的 Issue Key>,
  attachments = "<screenshot_path>"
)
```
**文件不存在**时：在 `bugs-reported.json` 中将该条目的 `screenshot` 字段置为 `null`，并在 Step 7 输出中列出"附件上传失败"条目。

## Step 6：保存产物

将上报结果写入 `reports/bugs-reported.json`：
```json
[
  {
    "title": "登录按钮点击后页面无响应",
    "jira_key": "PROJ-456",
    "severity": "CRITICAL",
    "assignee": "zhangsan",
    "screenshot": "reports/screenshots/login-fail.png"
  }
]
```

读取 `reports/artifacts.json`（不存在则初始化为 `{}`），合并写入：
```json
{ ...existing, "bugs": "reports/bugs-reported.json" }
```
写回 `reports/artifacts.json`。

## Step 7：告知用户

输出：
- 成功上报 N 条，JIRA Keys：[PROJ-456, PROJ-457, ...]
- 跳过/失败的条目
- 建议下一步：执行 `/ai-testing:test-report` 生成测试报告
