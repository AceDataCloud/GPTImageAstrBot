# AstrBot 的 GPT Image 插件

通过自己的 Ace Data Cloud 账号在 AstrBot 聊天中生成一张 GPT Image 2 图片。`gpt_image_generate` 异步提交一次任务；`gpt_image_get_task` 按**同一个 task ID** 查询直到完成。提交成功或出现预览链接不等于最终图片。

[English guide](../README.md) · [GPT Image API](https://platform.acedata.cloud/documents) · [当前价格](https://platform.acedata.cloud/models)

## 1. 搜索并安装

在 AstrBot WebUI 打开 **Extensions → Plugins → AstrBot Plugin Market**，搜索 **GPT Image**。核对卡片 **GPT Image by Ace Data Cloud**、作者 **acedatacloud** 和当前 GPT Image 服务图标。点击 **Install**，再到 **Installed** 确认插件已启用且没有加载错误。

AstrBot Cloud 尚未正式上架。源码合并发布后，可通过 **Installed → Install (+) → Install from URL** 填入 `https://github.com/AceDataCloud/GPTImageAstrBot` 预览。URL 安装不能算官方市场发现或安装通过。

## 2. 获取生成与查询权限的 Key

登录 [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications)，打开 **General application** 复制 Key，或进入 **Manage Keys → Create** 创建 AstrBot 专用 Key。服务专用 Key 必须同时允许 `/openai/images/generations` 和 `/openai/tasks`。生成前检查模型权限、当前价格与余额。

只复制 Key 本身，不加 `Bearer `，也不要使用 `platform-...` 管理 Token。不要把 Key 写进聊天消息或仓库。

## 3. 配置 AstrBot

在 **Extensions → Plugins → Installed** 点击 **GPT Image by Ace Data Cloud** 的齿轮，将 Key 填入 **Ace Data Cloud generation API key with GPT Image access** 并保存。WebUI 会遮蔽输入，但 AstrBot 数据目录仍存原值，应保护该目录。

选择支持工具调用的聊天模型，在当前 Profile 和 Persona 中允许 `gpt_image_generate` 与 `gpt_image_get_task`。工具未出现时查看 **Extensions → Handlers**。

## 4. 在聊天中只提交一次

向机器人发送：

> 只调用一次 `gpt_image_generate`，生成一张纯米色背景上的蓝色纸球，干净的棚拍照片，不含文字，并告诉我返回的 task ID。

首版固定使用 `model=gpt-image-2`、`size=1024x1024`、`quality=low`，生成一张 PNG URL 图片。插件不会自动换模型或在网络错误后重复付费提交。工具返回 `status: submitted` 和 `task_id`，请保存该 ID。

## 5. 查询同一 task ID

继续发送：

> 使用 `gpt_image_get_task` 查询任务 ID `<刚才的 task_id>`，不要再生成图片，告诉我状态和最终链接。

返回 `pending` 时稍后继续查**同一个 ID**。插件不会返回预览图片。只有 `status: succeeded` 且 `success: true` 才返回最终 `image_urls`。打开链接检查图片。若模型想再次提交，请停止并明确只调用查询工具。

## 6. 核对账单与排障

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
