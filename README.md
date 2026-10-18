# GPT Image for AstrBot

Generate one GPT Image 2 image in AstrBot chat through your own Ace Data Cloud account. `gpt_image_generate` submits one asynchronous job; `gpt_image_get_task` queries the **same task ID** until it succeeds. A submitted job or preview URL is not a final image.

**This PR targets 0.1.1** with native help/admin lookup commands, bilingual configuration and illustrated setup. Existing 0.1.0 installations do not gain these entries until the source is merged and the package is published/updated.

This independent **GPT Image integration is provided by Ace Data Cloud**. It is not an official plugin from the GPT Image publisher or the AstrBot team. Use your own Ace account and API key.

[简体中文指南](readme/README_zh_Hans.md) · [GPT Image API](https://platform.acedata.cloud/documents?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_documents) · [Current prices](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_pricing)

## 1. Find and install

Current upstream navigation (2026-10-18): **Plugins → Plugins → Plugin Market / Installed**. The earlier tested 4.28.2 English UI may label the section Extensions. Configure this service in the installed plugin gear; **do not paste its key into model-provider settings**.

**Publication status (2026-10-18): not yet listed in the official market.** After publication, open [AstrBot Cloud Plugin Market](https://cloud.astrbot.app/market), search **GPT Image**, and verify **GPT Image by Ace Data Cloud / acedatacloud**. For the current preview, use the repository URL below; a repository install is not official market publication.

The AstrBot Cloud listing has not yet been published. The source release is merged; use **Plugins → Plugins → Installed → Install Plugin (+) → Install from URL** with `https://github.com/AceDataCloud/GPTImageAstrBot` for a preview. URL installation does not prove official market discovery or installation.

## 2. Get a key with image and task access

[Register or sign in to Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_signup) first. Initialize **General application** if it does not exist. The following images show the shared Ace Applications page, not AstrBot.

Sign in at [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_readme_api_key). Open **General application** to copy a key, or **Manage Keys → Create** to make an AstrBot-specific key. A service-specific key must allow both `/openai/images/generations` and `/openai/tasks`. Check current model access, pricing, and balance before generating.

Copy the key value only. Do not add `Bearer ` or use a `platform-...` management token. Never put the key in a chat prompt or repository file.

1. Open **General application**. Use **1** to copy the existing key, or **2 Manage Keys → Create** for a dedicated key.

![Copy an Ace key or open Manage Keys (redacted)](_assets/tutorial/get-api-key-en.png)

2. Use a name such as `AstrBot GPT Image`. Set expiry/limits as needed and allow both `/openai/images/generations` and `/openai/tasks`. The screenshot’s Dify tutorial name is an older example.

![Create an optional dedicated key (shared Ace page, not AstrBot)](_assets/tutorial/create-api-key-en.png)

Images reused and checked on 2026-10-18; original capture dates were not supplied. Credentials and balance are redacted. [Sources and version limits](_assets/tutorial/sources.json).

### Where to paste it in AstrBot

Open **Plugins → Plugins → Installed**, select the gear on **GPT Image by Ace Data Cloud**, paste the key into **Ace Data Cloud generation API key with GPT Image access** (stored as `api_key`), and save. No `Bearer ` prefix; never paste the key in chat.

![AstrBot official historical plugin configuration reference, not this plugin running](_assets/tutorial/astrbot-plugin-config-reference.png)

This is the official AstrBot `helloworld` configuration example, labelled v3.4.14 (build v3.4.9), not an Ace setup or run. The instructions above identify this plugin’s exact field and current navigation; later UI layouts may differ.

## 3. Configure AstrBot

Under **Plugins → Plugins → Installed**, select the gear icon for **GPT Image by Ace Data Cloud**. Enter the key in **Ace Data Cloud generation API key with GPT Image access** and save. The WebUI masks the field, but the AstrBot data directory stores the original value; protect that directory.

Choose a chat model that supports tool calling and allow `gpt_image_generate` and `gpt_image_get_task` for the active profile and persona. Check **Plugins → Manage Behaviors → Function Tools** if a tool is unavailable.

## Native commands without a chat model

| Input | Result |
| --- | --- |
| `/gptimage_ace` | Show service, Token setup and lookup help; no external API call. |
| `/gptimage_ace_task <task_id>` | AstrBot administrators only: retrieve one existing task, with status/final media; no LLM or generation. |

Commands use the default `/` prefix; adapt it if your instance uses another wake prefix. AstrBot enforces administrator identity. The instance shares this plugin key, so direct lookup is administrator-only; other users use Agent tools allowed by their profile/persona. For `pending`, query the same ID later; for `failed`, inspect the original task/trace.

## 4. Submit one generation in chat

Ask the bot:

> Call `gpt_image_generate` exactly once to make a single blue paper sphere on a plain cream background, clean studio photograph, no text. Tell me the returned task ID.

This first version fixes `model=gpt-image-2`, `size=1024x1024`, `quality=low`, and one PNG URL result. It does not change models automatically or repeat a paid generation after a network error. The tool returns `status: submitted` with a `task_id`; save it.

## 5. Query that task ID

Ask the bot:

> Use `gpt_image_get_task` for task ID `<the exact task_id>`. Do not generate another image. Report the status and final image URL.

If status is `pending`, wait and query the **same ID** again. The plugin withholds preview images. Only `status: succeeded` with `success: true` returns final `image_urls`. Open the returned URL to inspect the image. If the bot tries to submit a second job, stop it and request only the task lookup tool.

## 6. Check billing and troubleshoot

### Cancelled tasks and interrupted waiting

An explicit failed/cancelled/rejected task is terminal: the plugin returns `status: failed`, `success: false` and no media, even if `finished_at` is still empty. It does not resubmit. Cancelling a local chat/command stops waiting locally; it does **not** cancel an upstream generation, and an already-started HTTP request may still finish. Inspect the original task/history and keep the same ID; there is no upstream-cancel command in this plugin.

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

## Reproduce the no-cost host check

From this repository in an isolated Python 3.12 environment:

```bash
uv venv --python 3.12 .venv-host
uv pip install --python .venv-host/bin/python astrbot==4.29.0
.venv-host/bin/python scripts/verify_host.py
```

The check needs no API Key and starts no server. It imports real AstrBot
decorators, registers both commands/two tools, checks admin/non-admin access,
masked-key schema, missing-Key handling and cancellation propagation with
socket access blocked. Fake events and mocked cancellation do not establish
a full message-dispatcher, market install, live generation, task ownership,
new billing or signup/conversion result. Use normal `python -m pytest -q`
for transport and command regression tests.
