# wjkc.lol 自动签到脚本 v2.0

这是一个基于 GitHub Actions 的智能自动化脚本，为您的 `wjkc.lol` 账户提供每日自动签到服务，具备智能token管理和通知去重功能。

## ✨ 主要特性

- **🔄 智能Token管理**: 15天周期自动更新token，优先使用现有token，失效时自动登录获取新token
- **🚫 通知去重机制**: 防止同一天内重复发送通知，避免消息轰炸
- **👥 多账户支持**: 支持多个账户同时管理，统一签到和通知
- **📱 专业通知系统**: 使用telegram-action发送详细的签到报告，包含任务链接
- **🛡️ 完全自动化**: 基于 GitHub Actions，无需手动干预，智能处理各种异常情况


## ⚙️ 核心原理

本脚本采用**智能Token管理策略**：
- **15天周期检查**: 自动检测token是否需要更新，避免频繁登录
- **优先级策略**: 优先使用现有token，仅在失效时才进行登录
- **去重机制**: 同一天内只发送一次通知，避免重复消息
- **统一工作流**: 合并原有的重复工作流，确保单一执行点

## 🚀 部署指南

请严格按照以下步骤进行配置，以确保自动化流程能够成功运行。

### 第1步：Fork 本仓库

点击本页面右上角的 **`Fork`** 按钮，将此仓库复制到您自己的 GitHub 账户下。接下来的所有操作都在您自己的仓库中进行。

### 第2步：设置 GitHub Secrets

进入您Fork后的仓库，点击 `Settings` -> `Secrets and variables` -> `Actions`。然后点击 `New repository secret`，添加以下机密信息：

-   **`WJKC_CREDENTIALS`**:
    -   **Name**: `WJKC_CREDENTIALS`
    -   **Value**: 您的 `wjkc.lol` 账户凭据，**JSON 格式的字符串**。
        *   **示例**:
            ```json
            [{"name": "MyAccount1", 
              "username": "your_username1", 
              "password": "your_password1"}, 
            {"name": "MyAccount2",
              "username": "your_username2",
              "password": "your_password2"}]
            ```
           `name` 字段是可选的，用于在日志中标识账户。
           请确保 `username` 和 `password` 字段正确。

-   **`GH_TOKEN`**:
    -   **Name**: `GH_TOKEN`
    -   **Value**: 一个具有 `repo` 权限的 GitHub Personal Access Token (PAT)。此 Token 用于脚本自动更新仓库中的 `WJKC_TOKENS` 机密。
        *   **如何获取**: 前往 GitHub `Settings` -> `Developer settings` -> `Personal access tokens` -> `Tokens (classic)` -> `Generate new token`。确保勾选 `repo` 权限。

-   **`WJKC_TOKENS`** (可选):
    -   **Name**: `WJKC_TOKENS` (请注意是复数`S`)
    -   **Value**: 您现有的 `wjkc.lol` token，以逗号(`,`)分隔。
        *   **用途**: 如果通过登录获取新 token 失败，脚本将回退到使用此处的 token 进行签到。
        *   **格式示例**: `cookie_value_of_account_1,cookie_value_of_account_2`

-   **`TELEGRAM_TOKEN`** (推荐):
    -   **Name**: `TELEGRAM_TOKEN`
    -   **Value**: 您的Telegram机器人的Token，用于发送详细的签到通知。

-   **`TELEGRAM_TO`** (推荐):
    -   **Name**: `TELEGRAM_TO`
    -   **Value**: 您的Telegram用户ID或频道的ID，用于接收通知。

> **注意**: 新版本使用 `TELEGRAM_TOKEN` 和 `TELEGRAM_TO` 替代了原来的 `BOT_TOKEN` 和 `CHAT_ID`，提供更专业的通知服务。

### 第3步：启动自动化

设置完Secrets后，您的自动化方案已经配置完毕。您可以等待第二天的定时任务自动运行，或者：

1.  进入仓库的 **`Actions`** 标签页。
2.  在左侧选择 **`WJKC Auto Checkin (Unified)`**。
3.  点击 **`Run workflow`** 按钮来手动触发一次，以立即验证您的配置是否成功。

## 📝 文件结构

-   **`.github/workflows/wjkc-auto-checkin.yml`**: 统一的GitHub Actions工作流，集成智能token管理和专业通知系统。
-   **`auto_checkin.py`**: 增强的核心脚本，支持智能token管理、去重机制和详细的结果收集。
-   **`get_token.py`**: 登录模块，负责通过用户凭据获取新的token。
-   **`update_github_secret.py`**: GitHub API集成模块，负责更新仓库机密。

## 🆕 v2.0 新特性

- **🔄 智能Token管理**: 15天周期自动检查和更新token
- **🚫 通知去重**: 同一天内只发送一次通知，避免消息轰炸
- **📊 详细统计**: 提供签到成功率、总奖励等统计信息
- **🔗 任务链接**: 通知中包含GitHub Actions任务详情链接
- **⚡ 统一工作流**: 合并重复的工作流，提高执行效率

## ⚠️ 重要说明

-   **智能管理**: v2.0版本采用15天周期的智能token管理，大幅减少不必要的登录操作。
-   **去重保护**: 内置通知去重机制，确保每天最多只发送一次通知。
-   **向后兼容**: 如果新的登录流程失败，系统会自动回退到使用现有token。
-   **安全合规**: 本项目仅用于学习和技术交流，请遵守相关服务条款。

## 🔧 故障排除

### 重复通知问题
v2.0版本已完全解决重复通知问题：
- 合并了重复的工作流文件
- 添加了通知去重机制
- 实现了智能token管理

### Token更新失败
如果遇到token更新问题：
1. 检查 `WJKC_CREDENTIALS` 格式是否正确
2. 确认 `GH_TOKEN` 具有足够权限
3. 查看Actions日志获取详细错误信息

---

## 结果示例
我已经成功签到了五天了
如图，tg bot自动推送[image.png](/屏幕截图%202025-06-17%20145816.png)

## 🔧 常见问题（403 Forbidden 更新 Secrets 失败）

- 原因与修复要点：
  - 使用了 `GITHUB_TOKEN`：该令牌无法管理仓库 Secrets。请改用个人访问令牌 (PAT) 并通过工作流的 `secrets.GH_TOKEN` 传入。
  - PAT 权限不足：
    - 经典 PAT：勾选 `repo`（对私有仓库）或 `public_repo`（仅公共仓库）。
    - 细粒度 PAT：给目标仓库授予 “Actions: Read and write” 和 “Repository secrets and variables: Read and write”。
  - 仓库权限不足：PAT 对应账户需要在目标仓库至少具备维护者/管理员权限。
  - 组织 SSO：若仓库属于启用 SSO 的组织，需要在 PAT 的 “Authorized” 页面为该组织授予 SSO 访问。

脚本已在 `update_github_secret.py` 中输出更详细的 401/403 提示信息，便于定位具体原因。
