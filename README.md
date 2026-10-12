# GPT Image for AstrBot

Generate one GPT Image 2 image in AstrBot chat through your own Ace Data Cloud account. `gpt_image_generate` submits one asynchronous job; `gpt_image_get_task` queries the **same task ID** until it succeeds. A submitted job or preview URL is not a final image.

[简体中文指南](readme/README_zh_Hans.md) · [GPT Image API](https://platform.acedata.cloud/documents?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_documents) · [Current prices](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_pricing)

## 1. Find and install

In AstrBot WebUI, open **Extensions → Plugins → AstrBot Plugin Market** and search **GPT Image**. Check the card says **GPT Image by Ace Data Cloud**, the author is **acedatacloud**, and the icon matches the current GPT Image service. Select **Install**, then confirm that it is enabled without a load error under **Installed**.

The AstrBot Cloud listing has not yet been published. After the source release is merged, use **Installed → Install (+) → Install from URL** with `https://github.com/AceDataCloud/GPTImageAstrBot` for a preview. URL installation does not prove official market discovery or installation.

## 2. Get a key with image and task access

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

Sign in at [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_api_key). Open **General application** to copy a key, or **Manage Keys → Create** to make an AstrBot-specific key. A service-specific key must allow both `/openai/images/generations` and `/openai/tasks`. Check current model access, pricing, and balance before generating.

Copy the key value only. Do not add `Bearer ` or use a `platform-...` management token. Never put the key in a chat prompt or repository file.

## 3. Configure AstrBot

Under **Extensions → Plugins → Installed**, select the gear icon for **GPT Image by Ace Data Cloud**. Enter the key in **Ace Data Cloud generation API key with GPT Image access** and save. The WebUI masks the field, but the AstrBot data directory stores the original value; protect that directory.

Choose a chat model that supports tool calling and allow `gpt_image_generate` and `gpt_image_get_task` for the active profile and persona. Check **Extensions → Handlers** if a tool is unavailable.

## 4. Submit one generation in chat

Ask the bot:

> Call `gpt_image_generate` exactly once to make a single blue paper sphere on a plain cream background, clean studio photograph, no text. Tell me the returned task ID.

This first version fixes `model=gpt-image-2`, `size=1024x1024`, `quality=low`, and one PNG URL result. It does not change models automatically or repeat a paid generation after a network error. The tool returns `status: submitted` with a `task_id`; save it.

## 5. Query that task ID

Ask the bot:

> Use `gpt_image_get_task` for task ID `<the exact task_id>`. Do not generate another image. Report the status and final image URL.

If status is `pending`, wait and query the **same ID** again. The plugin withholds preview images. Only `status: succeeded` with `success: true` returns final `image_urls`. Open the returned URL to inspect the image. If the bot tries to submit a second job, stop it and request only the task lookup tool.

## 6. Check billing and troubleshoot

Use the returned trace ID in your Ace Data Cloud application usage history. For the verified `gpt-image-2` single-image route, the current source rule lists 0.11 Credits before account discounts; verify the live price before use. Task lookups retrieve the existing job.

| Symptom | Check |
| --- | --- |
| Plugin fails to load | AstrBot version, **Failed to Load Plugins**, then **Data & Logs → Logs**. |
| Tools do not appear | Plugin enabled; active profile/persona permit both tools; chat model supports tool calling. |
| HTTP 401 or 403 | Key type, expiry, model access, balance, and both paths in Allowed APIs. |
| Network error after submission | Check request history before retrying; a timed-out response may still have created a task. |
| Pending task | Query the same ID later; do not repeat `gpt_image_generate`. |
| Failed task | Inspect the original task or trace ID in service request history. |

The plugin sends the key only to `https://api.acedata.cloud`, rejects redirects, and makes no automatic paid retry. It uses Python's standard library and needs no extra package. Only submit content you have permission to process.

## Verified local run

In an isolated official AstrBot `v4.28.2` instance, ChatUI invoked generation exactly once, then used the same task ID to retrieve `succeeded` and one final image URL. The returned PNG was HTTP 200 and decoded as 1024×1024. One `ApiUsage` row exactly matched the returned trace: 0.11 Credits original, 0.099 Credits deducted. [Sanitized evidence](tests/e2e-results.json) records task, media, and usage. Official market discovery and installation remain open.

## Brand asset

`logo.png` is the unmodified current [GPT Image service icon](https://cdn.acedata.cloud/7dljuv.png), SHA-256 `b525d3451af82c229d95402f91a20e74bd8b738c75b77c12a2592cb1d02b344f`.
