---
name: gen-test-cases
description: 基于需求文档生成测试用例，可选接入 Figma 设计稿或应用截图作为 UI 参考，输出 XMind 格式文件。触发场景：用户提供需求文档、PRD，或要求生成测试用例时。
---

# 测试用例生成

## Step 1：收集必填输入

如果用户未提供需求文档，询问：

> "请提供需求文档（以下任一方式）：
> 1. 文件路径（支持 .md / .txt / .pdf）
> 2. 直接描述需求内容
> 3. Confluence 页面链接"

根据来源读取 PRD 内容：

- **本地文件（.md/.txt）**：使用 Read 工具直接读取
- **PDF 文件**：
  ```bash
  python3 -c "
  import pdfplumber, sys
  with pdfplumber.open(sys.argv[1]) as pdf:
      for page in pdf.pages:
          print(page.extract_text() or '')
  " <filepath>
  ```
- **Confluence 链接**：从 URL 的 `pageId=` 参数提取 page_id（如 `?pageId=283880951` → `283880951`）。
  如无法提取，询问用户"请直接提供 Confluence 页面 ID（纯数字）"。
  
  调用 `mcp__mcp-atlassian__confluence_get_page(page_id=..., convert_to_markdown=true)`

## Step 2：询问 UI 参考

> "是否有 UI 参考？（可提高用例字段名准确性）
> 1. Figma 链接（推荐）
> 2. 应用 URL（我会自动截图关键页面）
> 3. 无，仅基于文档生成"

### 有 Figma 链接

调用 `figma-to-markdown` skill，传入 Figma 链接，获取 UI 结构描述（组件名、字段标签、按钮文案）作为 `ui_context`。

### 有应用 URL

使用 Playwright MCP 访问应用：
1. 截图主页/首页
2. 导航到与需求相关的功能页面（根据 PRD 关键词判断）
3. 对关键功能页面截图（**总数上限 5 张**，优先级：登录成功页 > 核心功能入口页 > 发现异常的页面；达到上限后停止截图，继续执行后续步骤）
4. 将截图文件路径列表作为 `ui_context` 传入

截图存储路径：`reports/ui-screenshots/`

### 无 UI 参考

`ui_context` 设为空字符串，标记为降级模式。

## Step 3：确定 lib_path

Plugin 的 XMind 引擎位于当前 skill 同级的 `lib/` 目录：
```bash
# 获取 plugin 根目录（SKILL.md 上两级）
# ai-testing/skills/gen-test-cases/SKILL.md → 上两级 → ai-testing/
# lib_path = <plugin_root>/lib/gen_xmind_template.py
```

通过查找当前 SKILL.md 的位置推算 lib 路径，或使用：
```bash
find ~/.claude -name "gen_xmind_template.py" -path "*/ai-testing/*" 2>/dev/null | head -1
```

**如果 `lib_path` 为空，立即停止**，告知用户：
> "未找到 gen_xmind_template.py，请确认 ai-testing plugin 已正确安装到 `~/.claude/plugins/ai-testing/`"
不要继续执行 Step 4。

## Step 4：启动 test-designer

启动 `test-designer` subagent，传入：
- `prd_content`：Step 1 读取的需求文本
- `ui_context`：Step 2 获取的 UI 参考（Figma 描述/截图路径列表/空字符串）
- `output_path`：`reports/test-cases.xmind`
- `lib_path`：Step 3 确定的 gen_xmind_template.py 绝对路径

## Step 5：保存产物状态

读取 `reports/artifacts.json`（不存在则初始化为 `{}`），添加：
```json
{ "test-cases": "reports/test-cases.xmind" }
```
写回 `reports/artifacts.json`。

## Step 6：告知用户

输出 subagent 返回的用例摘要，并提示：
- 建议下一步：执行 `/ai-testing:run-tests` 进行自动化测试
