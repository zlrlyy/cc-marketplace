---
name: run-tests
description: 使用 Playwright MCP 驱动 Chrome 执行探索性测试和自动化测试，缓存登录态，截图记录失败。触发场景：用户提供应用 URL 并要求执行测试时。
---

# 测试执行

## Step 1：收集输入

询问被测应用 URL（如用户已提供则跳过）：
> "请提供被测应用 URL（如 https://staging.example.com）"

询问测试模式：
> "执行方式：
> 1. 探索性测试（AI 自主发现问题，适合首次测试）
> 2. 执行已有用例（需提供用例列表或使用 reports/test-cases.xmind 中的用例）
> 3. 两者都执行"

**如用户选择模式 2 或 3，追加询问用例数量：**
> "大约有多少条用例需要执行？"

- 若用例数量 **超过 20 条**，提示：
  > "用例较多时，逐条执行会比较慢。有两种方式可选：
  > - **当前模式（MCP）**：单浏览器串行执行，适合少量用例或探索性测试
  > - **并行模式（推荐）**：将用例写成 `.spec.ts` 文件，用 `npx playwright test --workers=4` 并行执行，速度可提升数倍
  >
  > 是否继续用当前 MCP 模式，还是需要帮你生成 `.spec.ts` 文件以并行执行？"

询问登录状态：
> "应用是否需要登录？
> 1. 需要
> 2. 不需要"

## Step 2：处理登录

如需要登录，优先读取环境变量 `TEST_USERNAME`、`TEST_PASSWORD`。

如未设置环境变量，提示用户：
> "**请勿直接在对话中粘贴密码**，建议先在终端设置环境变量：
> ```bash
> export TEST_USERNAME="your-username"
> export TEST_PASSWORD="your-password"
> ```
> 设置后重新执行本 skill，凭证将自动读取。
> 如确实无法使用环境变量，请仅提供账号，密码将在最小作用域内使用后立即丢弃。"

使用 Playwright MCP：
1. 导航到登录页
2. 填写账号密码（优先从 `TEST_USERNAME` / `TEST_PASSWORD` 读取），提交
3. 验证登录成功（检查页面 URL 变化或欢迎信息）
4. 后续操作将复用此登录状态（Playwright MCP 在同一会话中自动保持 cookie）

## Step 3：探索性测试（模式1/3）

### 阶段一：发现

使用 Playwright MCP 系统性浏览应用：
- 从首页/主入口开始
- 点击所有导航菜单和主要入口
- 记录发现的页面（URL、页面标题、主要功能描述）
- 截图保存到 `reports/screenshots/explore-<timestamp>-<序号>.png`（timestamp 格式：`YYYYMMDD-HHmmss`，每次执行取统一时间戳）

### 阶段二：复杂性评估

分析发现的页面，评估：
- 核心业务路径（登录→核心功能→结果）
- 高风险功能（数据修改、支付、权限相关）
- 复杂交互（多步骤表单、条件逻辑）

选出 3-5 个优先测试的功能点。

### 阶段三：执行测试

针对每个优先功能，测试：
- **主流程**：正常操作，验证预期结果
- **异常输入**：空值、超长字符串、特殊字符
- **边界值**：数字类字段的最大值、最小值

每次操作后截图，失败时记录错误信息。

## Step 4：执行已有用例（模式2/3）

### 解析 XMind 用例

如 `reports/test-cases.xmind` 存在，使用 `lib/parse_xmind.py` 解析：

```bash
python3 lib/parse_xmind.py reports/test-cases.xmind
```

返回结构化用例列表，每条格式：
```json
{
  "id": "TC001",
  "title": "用例名称",
  "module": "所属模块",
  "preconditions": ["前置条件"],
  "steps": ["操作步骤"],
  "expected": ["预期结果"]
}
```

按以下格式逐条执行：
1. 满足 `preconditions`（导航到正确页面、准备数据等）
2. 按 `steps` 操作
3. 对照 `expected` 验证结果（截图存证）
4. 记录 pass/fail

如 XMind 不存在，询问用户直接提供用例描述。

## Step 5：保存产物

将测试结果写入 `reports/playwright-results.json`：

```json
{
  "summary": {
    "total": 10,
    "passed": 8,
    "failed": 2,
    "executed_at": "2026-04-21T10:30:00"
  },
  "results": [
    {
      "name": "用户登录-主流程",
      "status": "passed",
      "steps": ["打开登录页", "输入账号密码", "点击登录"],
      "screenshot": "reports/screenshots/login-pass.png",
      "error": ""
    },
    {
      "name": "搜索功能-空关键词",
      "status": "failed",
      "steps": ["点击搜索框", "直接点击搜索按钮"],
      "screenshot": "reports/screenshots/search-empty-fail.png",
      "error": "期望显示'请输入关键词'提示，实际页面无响应"
    }
  ]
}
```

读取 `reports/artifacts.json`（不存在则初始化为 `{}`），合并写入：
```json
{ ...existing, "test-results": "reports/playwright-results.json" }
```
写回 `reports/artifacts.json`。

## Step 6：告知用户

输出：
- 测试通过率：X/N（X%）
- 失败用例列表（含截图路径）
- 建议下一步：执行 `/ai-testing:bug-report` 上报 Bug
