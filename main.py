"""GPT Image Agent tools for AstrBot."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import GPTImageClient, ImageError


class GPTImagePlugin(Star):
    """Submit an image job and retrieve its final image in chat."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        """Use AstrBot's masked-key plugin setting.

        Args:
            context: AstrBot plugin context.
            config: Plugin configuration.
        """
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="gpt_image_generate")
    async def gpt_image_generate(self, event: AstrMessageEvent, prompt: str) -> str:
        """Submit one GPT Image 2 generation; save its task ID for retrieval.

        Args:
            prompt(string): Description of the image to generate.

        Returns:
            JSON submission status and task ID, not a completed image.
        """
        try:
            result = await GPTImageClient(self.config.get("api_key", "")).submit(prompt)
        except ImageError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="gpt_image_get_task")
    async def gpt_image_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query the same GPT Image task ID until final success or failure.

        Args:
            task_id(string): Exact ID from gpt_image_generate.

        Returns:
            JSON status and image URLs only after terminal success.
        """
        try:
            result = await GPTImageClient(self.config.get("api_key", "")).query(task_id)
        except ImageError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)

    @filter.command("gptimage_ace")
    async def gptimage_ace_help(self, event: AstrMessageEvent):
        """Show GPT Image setup and existing-task help without an API call."""
        yield event.plain_result(
            "GPT Image by Ace Data Cloud / Ace Data Cloud 提供的 GPT Image 集成\nSetup / 配置：Plugins → Plugins → Installed → plugin gear / 插件 → 插件 → 已安装 → 齿轮。\nRegister/sign in / 注册登录：https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=gptimageastrbot_command_help\nGeneral application → Manage Keys → Create；首次先初始化通用应用。\nAllow APIs / 允许接口：/openai/images/generations + /openai/tasks。检查当前权限、余额和价格。\nPaste the API Key in plugin settings only, never in chat. / 只在插件设置填 Key，不在聊天发送密钥。\nAdmin existing-task lookup / 管理员查已有任务：/gptimage_ace_task <task_id>\nAgent lookup tool / Agent 查询工具：gpt_image_get_task；生成只调用一次，pending 时继续查同一 ID。\nGuide / 指南：https://github.com/AceDataCloud/GPTImageAstrBot#readme"
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("gptimage_ace_task")
    async def gptimage_ace_task(self, event: AstrMessageEvent, task_id: str):
        """Let administrators retrieve one existing task without an LLM or generation."""
        try:
            result = await GPTImageClient(self.config.get("api_key", "")).query(task_id)
        except ImageError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        yield event.plain_result(json.dumps(result, ensure_ascii=False))
