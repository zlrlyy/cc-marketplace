# ai-testing — AI 驱动全流程测试 Plugin

将 5 阶段测试流水线打包为 Claude Code Plugin：
**代码审查 → 用例设计 → 测试执行 → 缺陷管理 → 测试报告**

## 安装

### 第一步：克隆仓库

```bash
git clone <repo-url> ~/.claude/plugins/ai-testing
```

仓库已内置 `.claude-plugin/plugin.json` manifest，克隆后无需额外创建。


### 第二步：重启 Claude Code

重启后 plugin 自动加载，`/ai-testing` 系列指令即可使用。

## 使用方式

```bash
/ai-testing                    # 总入口，查看流水线状态并引导执行
/ai-testing:code-review        # 单独执行代码审查
/ai-testing:gen-test-cases     # 单独生成测试用例
/ai-testing:run-tests          # 单独执行测试
/ai-testing:bug-report         # 单独上报 Bug
/ai-testing:test-report        # 单独生成 HTML 报告
```

## MCP 依赖速查

| Skill | 依赖 MCP | 说明 |
|-------|---------|------|
| `run-tests` | Playwright MCP | 必须 |
| `gen-test-cases` | Playwright MCP | 可选，有应用 URL 时截图 |
| `gen-test-cases` | mcp-atlassian | 可选，PRD 来源为 Confluence 时 |
| `gen-test-cases` | Figma MCP | 可选，有 Figma 设计稿时 |
| `bug-report` | mcp-atlassian | 必须（上报 JIRA） |
| `code-review` | 无 | — |
| `test-report` | 无 | — |

## 前置配置

### 1. Playwright MCP（run-tests / gen-test-cases 需要）

在 `~/.claude/settings.json` 的 `mcpServers` 中添加：

```json
"playwright": {
  "command": "npx",
  "args": ["@playwright/mcp@latest"]
}
```

安装 Chromium：
```bash
npx playwright install chromium
```

### 2. mcp-atlassian（bug-report 必须 / gen-test-cases 可选）

支持 JIRA 和 Confluence，按需配置对应环境变量：

```json
"mcp-atlassian": {
  "command": "uvx",
  "args": ["mcp-atlassian"],
  "env": {
    "JIRA_SERVER_URL": "https://your-domain.atlassian.net",
    "JIRA_USERNAME": "your@email.com",
    "JIRA_API_TOKEN": "your-jira-api-token",
    "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
    "CONFLUENCE_USERNAME": "your@email.com",
    "CONFLUENCE_API_TOKEN": "your-confluence-api-token"
  }
}
```

> JIRA 和 Confluence 的 API Token 相同，在此处获取：https://id.atlassian.com/manage-profile/security/api-tokens
>
> 只用 JIRA（不需要读 Confluence PRD）时，可省略 `CONFLUENCE_*` 变量。
>
> **安全提示**：`~/.claude/settings.json` 是用户级配置，不在项目 git 仓库中，相对安全。如果将上述配置写入项目级 `.claude/settings.json`，请确保该文件已加入 `.gitignore`，避免 API Token 泄露到版本控制。

### 3. Figma MCP（gen-test-cases 可选）

仅在需要接入 Figma 设计稿生成更精准的用例时配置：

```json
"figma": {
  "command": "npx",
  "args": ["-y", "figma-developer-mcp", "--stdio"],
  "env": {
    "FIGMA_API_KEY": "your-figma-api-key"
  }
}
```

> 获取 Figma API Key：Figma → Settings → Security → Personal access tokens

### 4. Python 3 及依赖

```bash
python3 --version        # 需要 3.7+
pip3 install pdfplumber  # gen-test-cases 解析 PDF 需要
```

## 阶段产物

所有产物写入当前项目的 `reports/` 目录：

| 阶段 | 产物文件 |
|------|---------|
| 代码审查 | `reports/code-review.md` |
| 用例设计 | `reports/test-cases.xmind` |
| 测试执行 | `reports/playwright-results.json` |
| Bug 上报 | `reports/bugs-reported.json` |
| 测试报告 | `reports/report.html` |

## 与其他 Skills 的配合

- **`prd-breakdown`**（上游）：PRD 拆分后的需求可直接作为 `gen-test-cases` 的输入
- **`figma-to-markdown`**（集成）：`gen-test-cases` 阶段可选接入 Figma 设计稿提升用例准确性
- **`jira-to-dev`**（下游）：Bug 修复后可触发 `jira-to-dev` 完成开发闭环
