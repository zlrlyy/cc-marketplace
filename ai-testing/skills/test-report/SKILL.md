---
name: test-report
description: 汇总所有测试阶段产物，生成专业的自包含 HTML 测试报告（内联 CSS/JS，可直接分享）。触发场景：用户要求生成测试报告，或所有阶段完成后。
---

# 测试报告生成

## Step 1：扫描产物

读取 `reports/artifacts.json`（不存在则扫描 reports/ 目录下的已知文件名）。

检查每个文件是否实际存在：
```bash
ls reports/
```

展示产物状态：
```
📁 reports/ 目录产物：
  ✅ code-review.md       （代码审查已完成）
  ✅ test-cases.xmind     （测试用例已生成）
  ✅ playwright-results.json （测试执行已完成）
  ✅ bugs-reported.json   （Bug 已上报）
  ❌ report.html          （报告待生成）
```

## Step 2：收集环境信息（可选）

询问用户：
> "是否需要在报告中记录环境信息？如需要，请提供（直接回复'跳过'可忽略）：
> - 测试环境 URL
> - 应用版本号
> - 测试执行时间范围
> - 其他备注"

## Step 3：启动 report-generator

启动 `report-generator` subagent，传入：
- `artifacts`：各产物文件路径的 JSON 对象（只包含实际存在的文件）
- `output_path`：`reports/report.html`
- `env_info`：用户提供的环境信息（跳过则传空字符串）
- `report_schema`：报告必须包含的章节结构：
  ```json
  {
    "sections": ["执行摘要", "用例通过率", "失败用例详情", "Bug 列表（含 JIRA 链接）", "环境信息"],
    "constraints": ["HTML 自包含（内联 CSS/JS，无外部依赖）", "支持中文显示"]
  }
  ```

## Step 4：读取并更新 artifacts.json

读取 `reports/artifacts.json`，添加：
```json
{ "report": "reports/report.html" }
```
写回文件。

## Step 5：告知用户

输出：
- 报告已生成：`reports/report.html`
- 文件大小
- 打开命令：
  - macOS：`open reports/report.html`
  - Linux：`xdg-open reports/report.html`
  - Windows：`start reports/report.html`
