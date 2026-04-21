---
name: ai-testing
description: AI 测试流水线总入口。感知当前项目测试状态，引导用户完成「代码审查→用例设计→测试执行→缺陷管理→测试报告」完整流程，支持跳转到任意阶段单独执行。触发场景：用户发起测试任务、询问测试进度，或要求运行完整测试流程时。
---

# AI 测试流水线

## Step 1：检测流水线状态

检查 `reports/artifacts.json` 是否存在。

**如果存在**，读取内容，逐一检查每个产物文件是否实际存在：

```bash
ls reports/code-review.md reports/test-cases.xmind reports/playwright-results.json reports/bugs-reported.json reports/report.html 2>/dev/null
```

构建状态展示：
```
🔍 AI 测试流水线状态
─────────────────────────────────
  ✅ 阶段1：代码审查    reports/code-review.md
  ✅ 阶段2：用例设计    reports/test-cases.xmind
  ⏳ 阶段3：测试执行    未执行
  ⏳ 阶段4：Bug 上报    未执行
  ⏳ 阶段5：测试报告    未执行
─────────────────────────────────
```

**如果不存在**，显示全 ⏳ 初始状态。

## Step 2：引导用户操作

展示状态后询问：
> "请选择操作：
> 1. 从头开始（执行全部5个阶段）
> 2. 继续未完成的阶段（从第一个 ⏳ 阶段开始）
> 3. 跳转到指定阶段（输入数字）：
>    1) 代码审查
>    2) 用例设计
>    3) 测试执行
>    4) Bug 上报
>    5) 测试报告"

## Step 3：执行

各阶段与 skill 的映射关系：
- 阶段1：代码审查 → skill `code-review`
- 阶段2：用例设计 → skill `gen-test-cases`
- 阶段3：测试执行 → skill `run-tests`
- 阶段4：Bug 上报 → skill `bug-report`
- 阶段5：测试报告 → skill `test-report`

**选项1（从头开始）**：
使用 Skill 工具直接调用阶段1（`code-review`），无需用户手动输入命令。
阶段1完成后，询问用户是否继续阶段2，用户确认后再调用下一个 skill，依此类推。

**选项2（继续未完成）**：
找出第一个 ⏳ 阶段，使用 Skill 工具直接调用对应 skill。
该阶段完成后，询问用户是否继续下一阶段，用户确认后再继续。

**选项3（跳转指定阶段）**：
根据用户输入的数字，使用 Skill 工具直接调用对应 skill。

## 注意

- 使用 Skill 工具调用子 skill，**不要**展示命令让用户手动输入。
- 每个阶段完成后，**必须询问用户是否继续**下一阶段，而非自动连续执行。
- 所有实际分析工作由各子 skill（code-review / gen-test-cases 等）执行。
