# AstrBot 的 GPT Image 插件

通过自己的 Ace Data Cloud 账号在 AstrBot 聊天中生成一张 GPT Image 2 图片。`gpt_image_generate` 异步提交一次任务；`gpt_image_get_task` 按**同一个 task ID** 查询直到完成。提交成功或出现预览链接不等于最终图片。

**本 PR 的目标版本为 0.1.1**：新增原生帮助及管理员查询指令、双语配置和图文说明。合并和市场发布前，当前 0.1.0 安装不会自动获得这些入口。

这是 **Ace Data Cloud 提供的 GPT Image 独立集成**，不是 GPT Image 厂商或 AstrBot 团队的官方插件。使用自己的 Ace 账号和 API Key；不要填写其他平台的密钥。

[English guide](../README.md) · [GPT Image API](https://platform.acedata.cloud/documents?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_documents) · [当前价格](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_pricing)

## 1. 搜索并安装

当前上游文档（2026-10-18）：侧栏 **插件 → 顶部插件 → 插件市场 / 已安装**；旧 4.28.2 英文界面可能显示 Extensions。插件参数在已安装卡片齿轮里设置，**不要把服务插件 Key 填进模型提供商**。

**发布状态（2026-10-18）：尚未在官方市场上架。** 正式发布后，先打开 [AstrBot Cloud 插件市场](https://cloud.astrbot.app/market)，搜索 **GPT Image**，再核对 **GPT Image by Ace Data Cloud / acedatacloud**。当前请用下面的 Git 仓地址手动安装；不要把仓库安装说成官方市场收录。

AstrBot Cloud 尚未正式上架。源码已合并，可通过 **Plugins → Plugins → Installed → Install Plugin (+) → Install from URL** 填入 `https://github.com/AceDataCloud/GPTImageAstrBot` 预览。URL 安装不能算官方市场发现或安装通过。

## 2. 获取生成与查询权限的 Key

先[注册或登录 Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_signup)；首次没有通用应用时，先初始化 **General application**。下图取自同一 Ace 应用管理页面，不是 AstrBot 界面。

登录 [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_api_key)，打开 **General application** 复制 Key，或进入 **Manage Keys → Create** 创建 AstrBot 专用 Key。服务专用 Key 必须同时允许 `/openai/images/generations` 和 `/openai/tasks`。生成前检查模型权限、当前价格与余额。

只复制 Key 本身，不加 `Bearer `，也不要使用 `platform-...` 管理 Token。不要把 Key 写进聊天消息或仓库。

1. 打开 **General application**，用图中 **1** 复制现有 Key，或点 **2 Manage Keys → Create** 创建专用 Key。

![复制 Ace Key 或管理专用 Key（已脱敏）](../_assets/tutorial/get-api-key-en.png)

2. 可把名称设为 `AstrBot GPT Image`，按需要设置到期/限额；Allowed APIs 同时包含 `/openai/images/generations` 和 `/openai/tasks`。截图的 Dify tutorial 只是旧示例名称。

![创建专用 Key（共享 Ace 页面，非 AstrBot）](../_assets/tutorial/create-api-key-en.png)

图片于 2026-10-18 复用核验，原始拍摄日期未提供；凭据与余额已脱敏。 [来源和版本边界](../_assets/tutorial/sources.json)。

### 在 AstrBot 粘贴的位置

打开 **插件 → 插件 → 已安装**，点击 **GPT Image by Ace Data Cloud** 卡片齿轮，把 Key 填入 **Ace Data Cloud generation API key with GPT Image access**（保存字段为 `api_key`）并保存。不要填 `Bearer `；也不要在聊天里输入 Key。

![AstrBot 官方历史插件配置参考，非本插件运行截图](../_assets/tutorial/astrbot-plugin-config-reference.png)

此图是 AstrBot 官方 `helloworld` 配置示例，界面标签 v3.4.14（构建 v3.4.9），不是 Ace 配置或运行证明。上方说明给出了本插件的准确字段和当前菜单；新版本布局可能不同。

## 3. 配置 AstrBot

在 **Plugins → Plugins → Installed** 点击 **GPT Image by Ace Data Cloud** 的齿轮，将 Key 填入 **Ace Data Cloud generation API key with GPT Image access** 并保存。WebUI 会遮蔽输入，但 AstrBot 数据目录仍存原值，应保护该目录。

使用 Agent 工具时，选择支持工具调用的聊天模型，在当前 Profile 和 Persona 中允许 `gpt_image_generate` 与 `gpt_image_get_task`。工具未出现时查看 **Plugins → Manage Behaviors → Function Tools**。

## 无需聊天模型的原生指令

| 输入 | 作用 |
| --- | --- |
| `/gptimage_ace` | 显示本服务、Token 配置和查询用法，不请求外部 API。 |
| `/gptimage_ace_task <task_id>` | 仅 AstrBot 管理员：查询一个已有任务，返回状态与最终媒体，不调用 LLM 或生成。 |

指令采用默认 `/` 前缀；自定义唤醒前缀时相应替换。管理员身份由 AstrBot 判断；同一实例的插件 Key 是共享配置，因此查询指令默认限管理员。其他用户继续使用受当前人格/配置允许的 Agent 工具。`pending` 时稍后只查同一编号，`failed` 时按原 task/trace 排查。

## 4. 在聊天中只提交一次

向机器人发送：

> 只调用一次 `gpt_image_generate`，生成一张纯米色背景上的蓝色纸球，干净的棚拍照片，不含文字，并告诉我返回的 task ID。

首版固定使用 `model=gpt-image-2`、`size=1024x1024`、`quality=low`，生成一张 PNG URL 图片。插件不会自动换模型或在网络错误后重复付费提交。工具返回 `status: submitted` 和 `task_id`，请保存该 ID。

## 5. 查询同一 task ID

继续发送：

> 使用 `gpt_image_get_task` 查询任务 ID `<刚才的 task_id>`，不要再生成图片，告诉我状态和最终链接。

返回 `pending` 时稍后继续查**同一个 ID**。插件不会返回预览图片。只有 `status: succeeded` 且 `success: true` 才返回最终 `image_urls`。打开链接检查图片。若模型想再次提交，请停止并明确只调用查询工具。

## 6. 核对账单与排障

### 任务取消与本地中断

任务明确 failed/cancelled/rejected 时视为终态：即使 `finished_at` 尚未填入，也返回 `status: failed`、`success: false`，不显示媒体、不重新提交。本地取消聊天或指令只中断等待，**不会取消服务端生成**，已开始的 HTTP 请求仍可能完成。保留原 task ID 并查请求历史；本插件没有服务端取消任务指令。

在 Ace Data Cloud 应用用量中按返回的 trace ID 精确核对。经验证的 `gpt-image-2` 单张路径当前源码规则标价 0.11 Credits，账户折扣另计；调用前仍须核对线上价格。任务查询读取已存在的任务。

| 现象 | 检查项 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**Failed to Load Plugins**、**Data & Logs → Logs**。 |
| 看不到工具 | 插件已启用；当前 Profile/Persona 允许两个工具；模型支持工具调用。 |
| HTTP 401/403 | Key 类型、有效期、模型权限、余额及两个 Allowed APIs 路径。 |
| 提交后网络错误 | 重试前查请求历史；超时请求仍可能已创建任务。 |
| 任务 pending | 稍后查同一 ID，不重复调用生成工具。 |
| 任务 failed | 用原 task/trace ID 查服务请求历史。 |

插件只向 `https://api.acedata.cloud` 发送 Key，拒绝重定向，不自动重试付费生成。使用 Python 标准库，无新增依赖。只提交自己有权处理的内容。

## 已验证的本地运行

隔离的官方 AstrBot `v4.28.2` 中，ChatUI 只调用一次生成工具，再按同一 task ID 查询到 `succeeded` 和一个最终图片链接。PNG 链接 HTTP 200、解码为 1024×1024；一条 `ApiUsage` 按返回 trace 精确匹配，原价 0.11 Credits、实际扣 0.099 Credits。[脱敏证据](../tests/e2e-results.json)记录 task、媒体和用量。官方市场搜索与安装仍待完成。

## 品牌素材

`logo.png` 是未修改的当前 [GPT Image 服务图标](https://cdn.acedata.cloud/7dljuv.png)，SHA-256 为 `b525d3451af82c229d95402f91a20e74bd8b738c75b77c12a2592cb1d02b344f`。

## 复现免费宿主检查

在本仓库中使用独立 Python 3.12 环境：

```bash
uv venv --python 3.12 .venv-host
uv pip install --python .venv-host/bin/python astrbot==4.29.0
.venv-host/bin/python scripts/verify_host.py
```

无需 API Key，不启动服务。检查导入真实 AstrBot 装饰器、注册两个指令/两个工具，
验证管理员允许/非管理员拒绝、Key 遮罩 schema、空 Key 错误与取消传播，并阻止 socket 连接。
事件和取消为测试替身，不能据此声称完整消息分发、官方市场安装、真实生成、任务归属、
新账单或注册转化已验。传输和指令回归使用常规 `python -m pytest -q`。
